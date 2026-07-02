## Summary

Describe the change in 2-5 lines.

## Type

- [ ] feat
- [ ] fix
- [ ] docs
- [ ] chore

## Branch and Target

- Source branch: `feature/...` or `hotfix/...`
- Target branch: `dev` (default) or `main` (hotfix only)

## Validation

- [ ] Fresh Mint 22.3 install run completed (if installer-impacting)
- [ ] `sudo python3 main.py --profile default` succeeded
- [ ] No duplicate apt repos, timers, or desktop launchers after rerun
- [ ] Post-install README checklist items validated where relevant
- [ ] Logs reviewed for failures (`install.log` and `install-summary.txt`)

## Manual Checks (If Applicable)

- [ ] Wallpaper applied
- [ ] Cinnamon favorites/pinned launchers applied
- [ ] Firefox profile seeded and bookmarks imported
- [ ] UFW active with expected rules
- [ ] ClamAV timer installed and enabled
- [ ] Core CLI tools available (`sherlock`, `theHarvester`, `shodan`, `recon-ng`, `zbarimg`)

## Notes / Risks

List any risk, regression possibility, or follow-up work.
