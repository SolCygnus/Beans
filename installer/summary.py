from __future__ import annotations

from pathlib import Path

from installer.context import InstallerContext, TaskResult


def record_result(ctx: InstallerContext, task_id: str, status: str, details: str, fatal: bool = False) -> None:
    ctx.results.append(TaskResult(task_id, status, details, fatal=fatal))
    ctx.logger.info("%s [%s] %s", task_id, status, details)


def record_note(ctx: InstallerContext, note: str) -> None:
    ctx.notes.append(note)
    ctx.logger.info("NOTE %s", note)


def write_summary(ctx: InstallerContext) -> Path:
    summary_path = ctx.log_dir / "install-summary.txt"
    lines = [
        "Beans install summary",
        "",
        f"Profile: {ctx.profile}",
        f"Dry run: {'yes' if ctx.dry_run else 'no'}",
        "",
        "Tasks:",
    ]
    for result in ctx.results:
        lines.append(f"- {result.id}: {result.status} - {result.details}")
    if ctx.notes:
        lines.extend(["", "Notes:"])
        lines.extend([f"- {note}" for note in ctx.notes])
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary_path
