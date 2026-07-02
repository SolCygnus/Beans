from __future__ import annotations

import re
from pathlib import Path
import shutil

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import ensure_directory_for_user, run_command, write_text


CUDA_TAGS = {
    "12.6": ["cu126", "cu124", "cu121"],
    "12.5": ["cu124", "cu121"],
    "12.4": ["cu124", "cu121"],
    "12.3": ["cu121", "cu118"],
    "12.2": ["cu121", "cu118"],
    "12.1": ["cu121", "cu118"],
    "11.8": ["cu118"],
}


def _detect_cuda_tags(ctx: InstallerContext) -> list[str]:
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        record_note(ctx, "nvidia-smi was not present in the guest, so Whisper is using CPU mode.")
        return []
    result = run_command(ctx, [nvidia_smi], check=False, capture_output=True)
    if result.returncode != 0:
        record_note(ctx, "nvidia-smi did not report a usable CUDA runtime, so Whisper is using CPU mode.")
        return []
    match = re.search(r"CUDA Version:\s+(\d+\.\d+)", result.stdout)
    if not match:
        record_note(ctx, "CUDA version was not detected from nvidia-smi, so Whisper is using CPU mode.")
        return []
    detected = match.group(1)
    return CUDA_TAGS.get(detected, ["cu124", "cu121", "cu118"])


def _validate_cuda(ctx: InstallerContext, python_path: Path) -> bool:
    result = run_command(
        ctx,
        [str(python_path), "-c", "import torch; print(torch.cuda.is_available())"],
        user=ctx.real_user,
        check=False,
        capture_output=True,
    )
    return result.stdout.strip() == "True"


def _free_gib(path: Path) -> int:
    usage = shutil.disk_usage(path)
    return int(usage.free / (1024 ** 3))


def install_whisper(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install Whisper and probe for CUDA support.")
        return
    venv_dir = ctx.user_home / ".local" / "share" / "beans" / "whisper-venv"
    ensure_directory_for_user(ctx, venv_dir.parent)
    python_path = venv_dir / "bin" / "python"
    if not venv_dir.exists():
        run_command(ctx, ["python3", "-m", "venv", str(venv_dir)], user=ctx.real_user)
    run_command(ctx, [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], user=ctx.real_user)

    gpu_active = False
    cuda_tags = _detect_cuda_tags(ctx)
    for tag in cuda_tags:
        install = run_command(
            ctx,
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "torch",
                "torchvision",
                "torchaudio",
                "--index-url",
                f"https://download.pytorch.org/whl/{tag}",
            ],
            user=ctx.real_user,
            check=False,
        )
        if install.returncode == 0 and _validate_cuda(ctx, python_path):
            gpu_active = True
            record_note(ctx, f"Whisper is configured for CUDA acceleration using {tag}.")
            break

    if not gpu_active:
        free_gib = _free_gib(ctx.user_home)
        if free_gib < 6:
            raise RuntimeError(f"Whisper needs more free disk for a CPU-only torch install. Available space: {free_gib} GiB.")
        run_command(
            ctx,
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "torch",
                "torchvision",
                "torchaudio",
                "--index-url",
                "https://download.pytorch.org/whl/cpu",
            ],
            user=ctx.real_user,
        )
        record_note(ctx, "Whisper fell back to CPU mode.")

    run_command(ctx, [str(python_path), "-m", "pip", "install", "openai-whisper"], user=ctx.real_user)
    run_command(ctx, [str(python_path), "-c", "import whisper"], user=ctx.real_user)
    write_text(
        Path("/usr/local/bin/beans-whisper"),
        f"#!/bin/sh\nexec {python_path} -m whisper \"$@\"\n",
        mode=0o755,
    )
