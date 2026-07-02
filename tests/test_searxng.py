from types import SimpleNamespace

from installer import runner, searxng
from installer.catalog import DEFAULT_COMPONENTS, SEARXNG_APT_PACKAGES
from installer.context import TaskResult


def test_searxng_is_enabled_by_default() -> None:
    component = next(item for item in DEFAULT_COMPONENTS if item.id == "searxng")
    assert component.default_enabled is True
    assert component.fatal is False


def test_searxng_build_dependencies_are_installed() -> None:
    expected = {
        "build-essential",
        "libffi-dev",
        "libssl-dev",
        "libxslt1-dev",
        "python3-dev",
        "zlib1g-dev",
    }
    assert expected.issubset(SEARXNG_APT_PACKAGES)


def test_runner_dispatches_searxng_installer(monkeypatch) -> None:
    calls = []
    context = object()
    monkeypatch.setattr(runner.searxng, "install_searxng", calls.append)

    runner.execute_component(context, "searxng")

    assert calls == [context]


def test_only_searxng_selects_one_component() -> None:
    args = runner.parse_args(["--only", "searxng"])
    assert runner.resolve_components(args) == ["searxng"]


def test_only_searxng_reports_failure() -> None:
    args = runner.parse_args(["--only", "searxng"])
    context = SimpleNamespace(results=[TaskResult("searxng", "failed", "installation failed", fatal=False)])
    assert runner.installer_exit_code(args, context) == 1


def test_default_install_preserves_nonfatal_failure_behavior() -> None:
    args = runner.parse_args([])
    context = SimpleNamespace(results=[TaskResult("searxng", "failed", "installation failed", fatal=False)])
    assert runner.installer_exit_code(args, context) == 0


def test_searxng_settings_are_local_only() -> None:
    settings = searxng._settings_content("test-secret")
    assert "use_default_settings: true" in settings
    assert 'bind_address: "127.0.0.1"' in settings
    assert "port: 8888" in settings
    assert 'secret_key: "test-secret"' in settings
    assert "limiter: false" in settings


def test_insecure_searxng_secrets_are_rotated() -> None:
    assert searxng._settings_need_secret_rotation('secret_key: "ultrasecretkey"')
    assert searxng._settings_need_secret_rotation('secret_key: "beans-searxng-local-only"')
    assert not searxng._settings_need_secret_rotation('secret_key: "generated-random-secret"')
    existing = 'instance_name: "Custom SearXNG"\nsecret_key: "ultrasecretkey"\n'
    rotated = searxng._rotate_insecure_secret(existing, "generated-random-secret")
    assert 'instance_name: "Custom SearXNG"' in rotated
    assert 'secret_key: "generated-random-secret"' in rotated


def test_searxng_launchers_include_health_checks() -> None:
    start_script = searxng._start_script()
    status_script = searxng._status_script()
    assert "SEARXNG_SETTINGS_PATH" in start_script
    assert "curl --silent --fail --head" in start_script
    assert "searx.webapp" in start_script
    assert "curl --silent --fail --head" in status_script
