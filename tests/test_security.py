from pathlib import Path
import subprocess
from types import SimpleNamespace

from installer import security


class RecordingLogger:
    def __init__(self) -> None:
        self.messages: list[tuple[str, tuple[object, ...]]] = []

    def info(self, message: str, *args: object) -> None:
        self.messages.append((message, args))


def _before_rules() -> str:
    return "\n".join(
        [
            "*filter",
            ":ufw-before-input - [0:0]",
            ":ufw-before-output - [0:0]",
            "COMMIT",
            "*nat",
            "COMMIT",
            "",
        ]
    )


def test_configure_ufw_issues_baseline_commands(monkeypatch) -> None:
    commands: list[list[str]] = []
    context = SimpleNamespace()
    monkeypatch.setattr(security, "_ensure_ufw_installed", lambda ctx: None)
    monkeypatch.setattr(security, "_ensure_icmp_before_rules", lambda ctx: None)

    def fake_run_command(ctx, command, **kwargs):
        commands.append(command)
        if command == ["ufw", "status"]:
            return subprocess.CompletedProcess(command, 0, stdout="Status: inactive\n", stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(security, "run_command", fake_run_command)

    security._configure_ufw(context)

    assert commands == [
        *[["ufw", *rule] for rule in security.BASELINE_UFW_RULES],
        ["ufw", "default", "deny", "incoming"],
        ["ufw", "default", "deny", "outgoing"],
        ["ufw", "default", "deny", "routed"],
        ["ufw", "logging", "on"],
        ["ufw", "status"],
        ["ufw", "--force", "enable"],
    ]


def test_icmp_rules_are_inserted_once_before_filter_commit(monkeypatch, tmp_path: Path) -> None:
    before_rules = tmp_path / "before.rules"
    before_rules.write_text(_before_rules(), encoding="utf-8")
    logger = RecordingLogger()
    context = SimpleNamespace(logger=logger)
    monkeypatch.setattr(security, "UFW_BEFORE_RULES", before_rules)

    security._ensure_icmp_before_rules(context)

    lines = before_rules.read_text(encoding="utf-8").splitlines()
    filter_commit = lines.index("COMMIT")
    assert lines[filter_commit - 2:filter_commit] == security.ICMP_RULES
    assert logger.messages[0][1][0] == before_rules

    security._ensure_icmp_before_rules(context)

    assert before_rules.read_text(encoding="utf-8").count(security.ICMP_RULES[0]) == 1
    assert before_rules.read_text(encoding="utf-8").count(security.ICMP_RULES[1]) == 1
