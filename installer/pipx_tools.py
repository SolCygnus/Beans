from __future__ import annotations

import json
from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import ensure_directory, run_command, which, write_text


PIPX_ENV = {
    "PIPX_HOME": "/opt/beans/pipx",
    "PIPX_BIN_DIR": "/usr/local/bin",
}
THEHARVESTER_REPO = "https://github.com/laramies/theHarvester.git"
RECON_NG_REPO = "https://github.com/lanmaster53/recon-ng.git"


def installed_tools(ctx: InstallerContext) -> set[str]:
    result = run_command(ctx, ["pipx", "list", "--json"], env=PIPX_ENV, check=False, capture_output=True)
    if result.returncode != 0 or not result.stdout.strip():
        return set()
    data = json.loads(result.stdout)
    return set(data.get("venvs", {}).keys())


def _pipx_python(ctx: InstallerContext) -> str:
    for candidate in ("python3.12", "python3.11", "python3.10", "python3"):
        if which(ctx, candidate):
            return candidate
    raise RuntimeError("No suitable Python 3 interpreter was found for pipx.")


def _ensure_pipx_root(ctx: InstallerContext) -> set[str]:
    if not ctx.dry_run:
        Path(PIPX_ENV["PIPX_HOME"]).mkdir(parents=True, exist_ok=True)
    return installed_tools(ctx)


def _verify_command(ctx: InstallerContext, command: str) -> None:
    run_command(ctx, ["bash", "-lc", f"{command} --help >/dev/null"], capture_output=True)


def install_sherlock(ctx: InstallerContext) -> None:
    known = _ensure_pipx_root(ctx)
    if "sherlock-project" not in known:
        run_command(ctx, ["pipx", "install", "--force", "sherlock-project"], env=PIPX_ENV)
    _verify_command(ctx, "sherlock")
    record_note(ctx, "Sherlock installed via pipx.")


def install_shodan(ctx: InstallerContext) -> None:
    known = _ensure_pipx_root(ctx)
    if "shodan" not in known:
        run_command(ctx, ["pipx", "install", "--force", "shodan"], env=PIPX_ENV)
    run_command(ctx, ["pipx", "runpip", "shodan", "install", "--force-reinstall", "setuptools<81"], env=PIPX_ENV)
    _verify_command(ctx, "shodan")
    record_note(ctx, "Shodan CLI installed via pipx, with setuptools pinned below 81 for pkg_resources compatibility.")


def install_theharvester(ctx: InstallerContext) -> None:
    known = _ensure_pipx_root(ctx)
    repo_dir = Path("/opt/beans/src/theHarvester")
    if not ctx.dry_run:
        ensure_directory(repo_dir.parent)
    if repo_dir.exists():
        run_command(ctx, ["git", "-C", str(repo_dir), "pull", "--ff-only"])
    else:
        run_command(ctx, ["git", "clone", THEHARVESTER_REPO, str(repo_dir)])
    if "theHarvester" not in known:
        run_command(ctx, ["pipx", "install", "--force", "--python", _pipx_python(ctx), str(repo_dir)], env=PIPX_ENV)
    else:
        run_command(ctx, ["pipx", "reinstall", "--python", _pipx_python(ctx), "theHarvester"], env=PIPX_ENV)
    _verify_command(ctx, "theHarvester")
    record_note(ctx, "theHarvester installed from its upstream repository.")


def install_recon_ng(ctx: InstallerContext) -> None:
    root = Path("/opt/beans/recon-ng")
    repo_dir = root / "app"
    venv_dir = root / "venv"
    python_path = venv_dir / "bin" / "python"
    if not ctx.dry_run:
        ensure_directory(root)
    if repo_dir.exists():
        run_command(ctx, ["git", "-C", str(repo_dir), "pull", "--ff-only"])
    else:
        run_command(ctx, ["git", "clone", RECON_NG_REPO, str(repo_dir)])
    if not venv_dir.exists():
        run_command(ctx, ["python3", "-m", "venv", str(venv_dir)])
    run_command(ctx, [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    requirements = repo_dir / "REQUIREMENTS"
    if requirements.exists():
        run_command(ctx, [str(python_path), "-m", "pip", "install", "-r", str(requirements)])
    write_text(
        Path("/usr/local/bin/recon-ng"),
        f"#!/bin/sh\nexec {python_path} {repo_dir / 'recon-ng'} \"$@\"\n",
        mode=0o755,
    )
    _verify_command(ctx, "recon-ng")
    record_note(ctx, "recon-ng installed from its upstream repository in a dedicated virtual environment.")
