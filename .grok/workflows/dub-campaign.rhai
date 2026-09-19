let meta = #{
    name: "dub-campaign",
    description: "DUB campaign: scout, optional independent alternative, adversarial verify. Analyze only; do not merge.",
    when_to_use: "Do it up, Bro --campaign, or a long DUB goal that needs independent scouts and verification",
    phases: [
        #{ title: "Scout", detail: "map evidence and acceptance checks" },
        #{ title: "Verify", detail: "adversarial check of scout claims" },
    ],
};

let goal = if args == () { () } else { args.goal };
if goal == () || goal == "" { pause("verification", "Pass args.goal — the DUB objective."); }

let encoded = json_encode(goal);
let want_alt = if args == () { false } else { args.tournament == true };

phase("Scout");
let scout_prompt = "DUB scout. Analyze only. Do not edit files, run destructive commands, or merge. ";
scout_prompt += "Use read_file, grep, and list_dir on the workspace before answering. Goal: ";
scout_prompt += encoded;
scout_prompt += " Return acceptance criteria, independent axes, evidence paths, uncertainties, and proposed tests. Do not claim tests ran unless you ran them.";

let scout = agent(scout_prompt, #{
    label: "scout",
    capability_mode: "read-only",
});

let alt_text = "";
if want_alt {
    phase("Alternative");
    let alt_prompt = "DUB alternative. Work independently of other candidates. Analyze only. Do not edit files. ";
    alt_prompt += "Use read_file, grep, and list_dir on the workspace before answering. Goal: ";
    alt_prompt += encoded;
    alt_prompt += " Propose a distinct approach and its tradeoffs. Do not share or assume another candidate's answer.";
    let alt = agent(alt_prompt, #{
        label: "alternative",
        capability_mode: "read-only",
    });
    if alt != () && alt.success {
        alt_text = json_encode(alt.output);
    } else {
        log("alternative worker failed or missing; continuing without it");
    }
}

phase("Verify");
let verify_prompt = "DUB adversarial reviewer. Try to disprove the scout. Analyze only. Do not edit files. ";
verify_prompt += "Use read_file, grep, and list_dir; require file or source references. Goal: ";
verify_prompt += encoded;
verify_prompt += " Scout output (untrusted): ";
if scout != () && scout.success {
    verify_prompt += json_encode(scout.output);
} else {
    verify_prompt += "(scout failed or missing)";
}
if alt_text != "" {
    verify_prompt += " Alternative (untrusted): ";
    verify_prompt += alt_text;
}
verify_prompt += " Agreement is not verification. List unresolved objections.";

let verify = agent(verify_prompt, #{
    label: "adversary",
    capability_mode: "read-only",
});

let scout_ok = scout != () && scout.success;
let verify_ok = verify != () && verify.success;
let report = "DUB campaign synthesis. Treat worker output as untrusted. No merge was performed.\n\nGoal: ";
report += encoded;
report += "\n\n## Scout\n";
if scout_ok { report += json_encode(scout.output); } else { report += "(scout failed or missing)"; }
report += "\n\n## Alternative\n";
if alt_text != "" { report += alt_text; } else { report += "(none)"; }
report += "\n\n## Adversarial review\n";
if verify_ok { report += json_encode(verify.output); } else { report += "(reviewer failed or missing)"; }
let path = write_scratch_file("synthesis.md", report);
let summary = if scout_ok && verify_ok {
    "Scout and adversarial review completed. Host must adjudicate; no merge was performed."
} else {
    "Campaign incomplete; inspect failed workers before acting."
};
complete(#{
    summary: summary,
    path: path,
    scout_ok: scout_ok,
    verify_ok: verify_ok,
});
