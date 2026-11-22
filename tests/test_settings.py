import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_settings(**env):
    clean = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
    return subprocess.run(
        [sys.executable, "-c", "import config.settings as s; print(s.DEBUG, s.ALLOWED_HOSTS)"],
        cwd=ROOT,
        env={**clean, **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_refuses_to_start_without_a_secret_key():
    result = run_settings()
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_production_with_a_secret_key():
    result = run_settings(DJANGO_SECRET_KEY="x" * 50, DJANGO_ALLOWED_HOSTS="a.example, b.example")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False ['a.example', 'b.example']"


def test_development_mode_needs_nothing():
    result = run_settings(DJANGO_DEBUG="1")
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("True")
