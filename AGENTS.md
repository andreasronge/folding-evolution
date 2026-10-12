See `CLAUDE.md` for project context, findings, tech stack, and conventions.

## Codex usage

- If the user asks to pre-register an experiment, log a result, promote a finding, scope-check claim language, supersede or retract a claim, run an FWER audit, or diagnose a failed experiment, read `.claude/skills/research-rigor/SKILL.md` and follow the matching mode.
- Treat the `research-rigor` skill as a manual workflow file, not an automatically invoked feature.
- Match on user intent, not exact wording. If the request could fit more than one mode, ask which mode they want before proceeding.
- When using the skill, follow its required templates, gates, and refusal conditions exactly.

## Local reference libraries

- Zotero local data dir on this machine: `/Users/andreasronge/Zotero`
- Zotero PDF/attachment storage: `/Users/andreasronge/Zotero/storage`
- Zotero profile prefs confirm `extensions.zotero.dataDir=/Users/andreasronge/Zotero`
- Attachments are stored under per-item key directories in `storage/`, not by collection path, so find papers by filename search or by querying `zotero.sqlite` when key-to-item mapping is needed.
