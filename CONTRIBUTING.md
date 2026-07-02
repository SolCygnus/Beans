# Contributing to Beans

## Branch Model

- `main`: stable, install-tested releases only
- `dev`: integration branch for approved changes
- `feature/<short-topic>`: normal work branches
- `hotfix/<short-topic>`: urgent fixes targeting `main`

## Workflow

1. Start from `dev`:
   ```bash
   git switch dev
   git pull
   git switch -c feature/<short-topic>
   ```
2. Open pull requests from `feature/*` into `dev`.
3. Promote `dev` into `main` only after full VM install validation.

## Commit Format

Use small, focused commits:

`type(scope): summary`

Examples:

- `feat(installer): add desktop asset refresh command`
- `fix(firefox): import toolbar bookmarks for fresh profiles`
- `docs(readme): clarify pre-install recommendations`

## Pull Request Titles

- `feat: <what changed>`
- `fix: <what changed>`
- `docs: <what changed>`
- `chore: <what changed>`

## Merge Requirements for `main`

- Fresh Linux Mint 22.3 VM install completes with `sudo python3 main.py --profile default`
- Post-install checklist in `README.md` passes
- No unintended asset drift in `assets/`
- No duplicate apt sources, timers, or desktop entries on rerun
- Logs reviewed for errors: `/var/log/beans/install.log` and `/var/log/beans/install-summary.txt`

## Scope Guardrails

- Avoid destructive git history operations on shared branches
- Prefer additive, reversible changes
