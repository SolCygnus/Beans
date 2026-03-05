from pathlib import Path


def test_main_entrypoint_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "main.py").is_file()


def test_installer_package_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "installer" / "__init__.py").is_file()
