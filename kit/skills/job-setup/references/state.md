# setup-state.json

Lives at the workspace root. Created by `install.sh`; `/job-setup` keeps it current.

```json
{
  "version": 1,
  "mode": "quick | full",
  "started": "YYYY-MM-DD",
  "stages": {
    "0_preflight": "done | partial | skipped | todo",
    "1_identity": "todo",
    "2_resume_import": "todo",
    "3_targets": "todo",
    "4_pay_answers": "todo",
    "5_rules": "todo",
    "6_voice": "todo",
    "7_accounts": "todo",
    "8_git": "todo",
    "9_tooling": "todo",
    "10_dry_run": "todo"
  },
  "choices": {
    "surface": "terminal | vscode",
    "os": "macos | linux",
    "github_remote": "none | private-repo-url",
    "second_git_identity": false,
    "sync_hooks": false,
    "easy_apply_submit": false,
    "portal_account_creation": false
  }
}
```

Rules: update the stage the moment it changes. `done` = every file for that stage written and checked. `partial` = some answers still `<ask>`. `skipped` = the user chose to skip. `/job-setup doctor` also scans for leftover `<...>` placeholders in `my-profile/SKILL.md`, `fill-form/references/answers.md`, `cold-email/references/voice.md` and `portal-apply/scripts/profile.json`.
