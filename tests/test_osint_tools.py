from installer import pipx_tools, runner, spiderfoot
from installer.catalog import DEFAULT_COMPONENTS


def test_holehe_is_enabled_by_default() -> None:
    component = next(item for item in DEFAULT_COMPONENTS if item.id == "holehe")
    assert component.default_enabled is True
    assert component.fatal is False


def test_runner_dispatches_holehe_installer(monkeypatch) -> None:
    calls = []
    context = object()
    monkeypatch.setattr(runner.pipx_tools, "install_holehe", calls.append)

    runner.execute_component(context, "holehe")

    assert calls == [context]


def test_holehe_uses_an_isolated_pipx_environment(monkeypatch) -> None:
    calls = []
    context = object()
    monkeypatch.setattr(pipx_tools, "_ensure_pipx_root", lambda ctx: set())
    monkeypatch.setattr(pipx_tools, "_pipx_python", lambda ctx: "python3.12")
    monkeypatch.setattr(pipx_tools, "run_command", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(pipx_tools, "record_note", lambda *args: None)

    pipx_tools.install_holehe(context)

    assert calls[0][0][1] == ["pipx", "install", "--force", "--python", "python3.12", "holehe"]
    assert calls[0][1]["env"] == pipx_tools.PIPX_ENV
    assert calls[1][0][1] == ["bash", "-lc", "holehe --help >/dev/null"]


def test_spiderfoot_launchers_include_health_checks() -> None:
    start_script = spiderfoot._start_script()
    status_script = spiderfoot._status_script()
    assert "127.0.0.1:5001" in start_script
    assert "curl --silent --fail" in start_script
    assert "spiderfoot.log" in start_script
    assert "curl --silent --fail" in status_script
    assert "spiderfoot.log" in status_script
