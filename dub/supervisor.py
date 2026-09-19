"""Bounded local CLI federation. Captured output is data, never executable authority."""

import json
import os
import selectors
import shutil
import signal
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .adjudicator import prepare
from .ledger import Ledger
from .providers.base import PROVIDERS, build_command, probe_compatibility
from .router import route, work_order
from .security import child_environment, redact
from .telemetry import parse_result

OUTPUT_LIMIT = 1_048_576  # bytes per stream; fail closed when exceeded


def now():
    return datetime.now(timezone.utc).isoformat()


def plan(config, goal, mode="federate", task_class="general", *, check_compatibility=False):
    if not goal.strip():
        raise ValueError("Goal must not be empty")
    available, skipped = [], []
    for key, settings in config.providers.items():
        provider = PROVIDERS.get(key)
        command = settings.command
        if command == "AUTO_DETECT" and provider:
            command = provider.executable
        reason = None
        if not settings.enabled:
            reason = "disabled"
        elif provider is None or not provider.headless:
            reason = provider.reason if provider else "unknown provider"
        elif not shutil.which(command):
            reason = "executable not found"
        elif check_compatibility:
            probe = probe_compatibility(key, os.path.abspath(shutil.which(command)))
            if not probe["compatible"]:
                reason = probe["reason"]
        if reason:
            skipped.append({"provider": key, "reason": reason})
        else:
            available.append(
                {
                    "provider": key,
                    "command": os.path.abspath(shutil.which(command)),
                    "model_requested": settings.model,
                    "effort_requested": settings.effort,
                    "sandbox": settings.sandbox,
                    "capabilities": list(provider.federation_capabilities),
                    "native_capabilities": list(provider.capabilities),
                    "compatibility": "compatible" if check_compatibility else "unchecked",
                }
            )
    assignments = route(available, goal, mode, task_class)
    for index, assignment in enumerate(assignments):
        assignment["wave"] = index // config.max_parallel_providers + 1
    # Validate requested provider knobs even on dry runs.
    for assignment in assignments:
        build_command(
            assignment["provider"],
            assignment["command"],
            work_order(goal, assignment),
            model=assignment["model_requested"],
            effort=assignment["effort_requested"],
            sandbox=assignment.get("sandbox", True),
        )
    return {
        "goal": redact(goal),
        "mode": mode,
        "task_class": task_class,
        "enabled": config.enabled,
        "max_parallel_providers": config.max_parallel_providers,
        "timeout_seconds": config.provider_timeout_seconds,
        "synthesis_provider": config.synthesis_provider,
        "assignments": assignments,
        "skipped": skipped,
    }


def _kill(proc):
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except ProcessLookupError:
        pass


def capture(
    argv, cwd, timeout, cancellation=None, *, environment=None, provider=None, grace_seconds=0
):
    """Drain both pipes concurrently with bounded memory, including hung descendants."""
    if os.name != "posix":
        raise RuntimeError("Federation currently requires POSIX process-group isolation")
    proc = subprocess.Popen(
        argv,
        cwd=cwd,
        env=child_environment(provider) if environment is None else environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    status, reason = "completed", None
    deadline = time.monotonic() + timeout
    stopping = False
    try:
        with selectors.DefaultSelector() as selector:
            for name, pipe in (("stdout", proc.stdout), ("stderr", proc.stderr)):
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while selector.get_map() or proc.poll() is None:
                if not stopping and cancellation is not None and cancellation.is_set():
                    status, reason = "interrupted", "run interrupted"
                if not stopping and status == "completed" and time.monotonic() >= deadline:
                    status, reason = "timeout", "provider timeout exceeded"
                if not stopping and status in {"timeout", "interrupted"}:
                    if not grace_seconds:
                        break
                    stopping = True
                    deadline = time.monotonic() + min(1.0, max(0, grace_seconds))
                    try:
                        os.killpg(proc.pid, signal.SIGINT)
                    except ProcessLookupError:
                        pass
                if stopping and time.monotonic() >= deadline:
                    break
                for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                    elif len(buffers[key.data]) + len(chunk) > OUTPUT_LIMIT:
                        status, reason = (
                            "output_limit",
                            "capture limit exceeded; partial output discarded",
                        )
                        break
                    else:
                        buffers[key.data].extend(chunk)
                if status == "output_limit":
                    break
    finally:
        # Also clean up background grandchildren after their root exits.
        _kill(proc)
        proc.wait()
        proc.stdout.close()
        proc.stderr.close()
    if status == "completed" and proc.returncode:
        status, reason = "failed", f"provider exited with code {proc.returncode}"
    if status == "output_limit":
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
    metadata = (
        parse_result(provider, buffers["stdout"].decode("utf-8", errors="replace"))
        if provider
        else {}
    )
    envelope_failure = metadata.pop("failure_reason", None)
    if status == "completed" and envelope_failure:
        status, reason = "failed", envelope_failure
    return {
        **metadata,
        "status": status,
        "failure_reason": reason,
        "return_code": proc.returncode,
        **{k: redact(v.decode("utf-8", errors="replace")) for k, v in buffers.items()},
    }


def run(config, goal, mode="federate", task_class="general", cancellation=None):
    cancellation = cancellation if cancellation is not None else threading.Event()
    if not config.enabled:
        raise ValueError("Federation is disabled in configuration")
    execution_plan = plan(config, goal, mode, task_class, check_compatibility=True)
    if not execution_plan["assignments"]:
        details = "; ".join(
            f"{item['provider']}: {item['reason']}" for item in execution_plan["skipped"]
        )
        raise ValueError(
            "No enabled providers with available safe headless executables"
            + (f" ({details})" if details else "")
        )
    run_id, started = uuid.uuid4().hex, now()
    run_dir = Path(config.run_dir).resolve() / run_id
    run_dir.mkdir(parents=True, mode=0o700)
    (run_dir / "plan.json").write_text(redact(json.dumps(execution_plan, indent=2)) + "\n")
    ledger = Ledger(run_dir / "ledger.sqlite3")
    run_record = dict(
        run_id=run_id, goal=goal, mode=mode, started_at=started, artifact_path=str(run_dir)
    )
    ledger.record_run(**run_record, status="running")

    def launch(assignment):
        provider = assignment["provider"]
        directory = run_dir / provider
        directory.mkdir(mode=0o700)
        workspace = directory / "workspace"
        workspace.mkdir(mode=0o700)
        prompt = work_order(goal, assignment)
        (directory / "work-order.txt").write_text(redact(prompt))
        record = dict(
            task_id=f"{run_id}:{provider}",
            run_id=run_id,
            provider=provider,
            harness=provider,
            role=assignment["role"],
            task_class=task_class,
            model_requested=assignment["model_requested"],
            effort_requested=assignment["effort_requested"],
            started_at=now(),
            artifact_path=str(directory),
            verification_result="not_performed",
        )
        ledger.record_task(**record, status="running")
        try:
            argv = build_command(
                provider,
                assignment["command"],
                prompt,
                model=assignment["model_requested"],
                effort=assignment["effort_requested"],
                sandbox=assignment.get("sandbox", True),
                **(
                    {"prompt_file": str(directory / "work-order.txt")} if provider == "grok" else {}
                ),
            )
            if cancellation.is_set():
                captured = {
                    "status": "interrupted",
                    "failure_reason": "cancelled before launch",
                    "return_code": None,
                    "stdout": "",
                    "stderr": "",
                }
            else:
                captured = capture(
                    argv,
                    workspace,
                    config.provider_timeout_seconds,
                    cancellation,
                    provider=provider,
                    grace_seconds=1 if provider == "claude" else 0,
                )
        except Exception as exc:
            captured = {
                "status": "failed",
                "failure_reason": redact(str(exc)),
                "return_code": None,
                "stdout": "",
                "stderr": "",
            }
        for stream in ("stdout", "stderr"):
            (directory / f"{stream}.txt").write_text(captured.pop(stream))
        result = {**record, **captured, "ended_at": now()}
        ledger.record_task(**result)
        (directory / "result.json").write_text(redact(json.dumps(result, indent=2)) + "\n")
        return result

    with ThreadPoolExecutor(max_workers=config.max_parallel_providers) as pool:
        futures = [pool.submit(launch, assignment) for assignment in execution_plan["assignments"]]
        try:
            results = [future.result() for future in futures]
        except KeyboardInterrupt:
            cancellation.set()
            # Pending workers write cancelled records without starting a CLI; running
            # captures see the event within 100ms and kill their process groups.
            results = [future.result() for future in futures]
        except BaseException:
            cancellation.set()
            ledger.record_run(**run_record, ended_at=now(), status="failed")
            raise
    successes = sum(item["status"] == "completed" for item in results)
    status = "completed" if successes == len(results) else "partial" if successes else "failed"
    if cancellation.is_set():
        status = "interrupted"
    prepare(run_dir, goal, results, config.synthesis_provider)
    ledger.record_run(**run_record, ended_at=now(), status=status)
    summary = {
        "run_id": run_id,
        "status": status,
        "run_dir": str(run_dir),
        "results": results,
        "synthesis_status": "awaiting_host_synthesis",
    }
    (run_dir / "summary.json").write_text(redact(json.dumps(summary, indent=2)) + "\n")
    return summary
