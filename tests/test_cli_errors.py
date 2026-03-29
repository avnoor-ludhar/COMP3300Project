import subprocess
import sys


def test_main_no_args_prints_usage_and_exits_nonzero(main_py):
    cp = subprocess.run(
        [sys.executable, str(main_py)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 1
    assert "Usage" in cp.stderr
    assert cp.stdout == ""


def test_main_extra_args_prints_usage_and_exits_nonzero(main_py, tmp_path):
    path = tmp_path / "in.json"
    path.write_text(
        '{"policy":"FIFO","jobs":[{"pid":"X","arrival":0,"burst":1,"priority":1}]}',
        encoding="utf-8",
    )
    cp = subprocess.run(
        [sys.executable, str(main_py), str(path), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 1
    assert "Usage" in cp.stderr
    assert cp.stdout == ""


def test_main_missing_input_file_exits_nonzero_with_stderr(main_py, tmp_path):
    missing = tmp_path / "does_not_exist_input.json"
    assert not missing.is_file()
    cp = subprocess.run(
        [sys.executable, str(main_py), str(missing)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode != 0
    assert cp.stdout == ""
    assert cp.stderr
    assert "FileNotFoundError" in cp.stderr


def test_main_malformed_json_exits_nonzero_with_stderr(main_py, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ not valid json", encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(main_py), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode != 0
    assert cp.stdout == ""
    assert cp.stderr
    assert "JSONDecodeError" in cp.stderr
