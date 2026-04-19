See `CLAUDE.md` for project context, findings, tech stack, and conventions.

## Codex usage

- If the user asks to pre-register an experiment, log a result, promote a finding, scope-check claim language, supersede or retract a claim, run an FWER audit, or diagnose a failed experiment, read `.claude/skills/research-rigor/SKILL.md` and follow the matching mode.
- Treat the `research-rigor` skill as a manual workflow file, not an automatically invoked feature.
- Match on user intent, not exact wording. If the request could fit more than one mode, ask which mode they want before proceeding.
- When using the skill, follow its required templates, gates, and refusal conditions exactly.
