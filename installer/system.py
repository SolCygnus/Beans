from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import urllib.request
from typing import Iterable

from installer.context import InstallerContext


def _trim_output(text: str, limit: int = 12000) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if len(stripped) <= limit:
        return stripped
    return stripped[-limit:]


def format_process_error(result: subprocess.CalledProcessError | subprocess.CompletedProcess[str]) -> str:
    stderr = _trim_output(getattr(result, "stderr", "") or "")
    stdout = _trim_output(getattr(result, "stdout", "") or "")
    if stderr:
        return stderr
    if stdout:
        return stdout
    return str(result)


def run_command(
    ctx: InstallerContext,
    command: Iterable[str],
    *,
    cwd: Path | None = None,
    user: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    command_list = list(command)
    if user:
        command_list = ["sudo", "-u", user, *command_list]
    ctx.logger.info("RUN %s", " ".join(shlex.quote(part) for part in command_list))
    if ctx.dry_run:
        return subprocess.CompletedProcess(command_list, 0, stdout="", stderr="")
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        result = subprocess.run(
            command_list,
            cwd=str(cwd) if cwd else None,
            env=full_env,
            text=True,
            check=check,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        stdout = _trim_output(exc.stdout or "")
        stderr = _trim_output(exc.stderr or "")
        if stdout:
            ctx.logger.error("STDOUT\n%s", stdout)
        if stderr:
            ctx.logger.error("STDERR\n%s", stderr)
        raise
    stdout = _trim_output(result.stdout or "")
    stderr = _trim_output(result.stderr or "")
    if stdout:
        ctx.logger.info("STDOUT\n%s", stdout)
    if stderr:
        ctx.logger.info("STDERR\n%s", stderr)
    return result


def ensure_directory(path: Path, mode: int = 0o755) -> None:
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(mode)


def ensure_directory_for_user(ctx: InstallerContext, path: Path, mode: int = 0o755) -> None:
    if ctx.dry_run:
        return
    run_command(ctx, ["mkdir", "-p", str(path)], user=ctx.real_user)
    path.chmod(mode)
    run_command(ctx, ["chown", "-R", f"{ctx.real_user}:{ctx.real_user}", str(path)])


def chown_path(ctx: InstallerContext, path: Path, *, recursive: bool = False) -> None:
    if ctx.dry_run or not path.exists():
        return
    command = ["chown"]
    if recursive:
        command.append("-R")
    command.extend([f"{ctx.real_user}:{ctx.real_user}", str(path)])
    run_command(ctx, command)


def write_text(path: Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(mode)


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default.copy() if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict, mode: int = 0o644) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n", mode=mode)


def copy_path(src: Path, dst: Path, *, ignore: set[str] | None = None) -> None:
    ignore = ignore or set()
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def download_to_file(ctx: InstallerContext, url: str, destination: Path, mode: int = 0o644) -> None:
    ctx.logger.info("DOWNLOAD %s -> %s", url, destination)
    if ctx.dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())
    destination.chmod(mode)


def package_installed(ctx: InstallerContext, package_name: str) -> bool:
    result = run_command(ctx, ["dpkg-query", "-W", "-f=${Status}", package_name], check=False, capture_output=True)
    return "install ok installed" in result.stdout


def which(ctx: InstallerContext, command_name: str, *, user: str | None = None) -> bool:
    result = run_command(ctx, ["bash", "-lc", f"command -v {shlex.quote(command_name)}"], user=user, check=False)
    return result.returncode == 0
