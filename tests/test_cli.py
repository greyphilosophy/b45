from __future__ import annotations

from io import StringIO

from b45.cli import _run, main


def run_cli(*args: str, stdin: str = "") -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = _run(args, stdin=StringIO(stdin), stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def test_encode_text_argument():
    exit_code, stdout, stderr = run_cli("encode", "Hello World")

    assert exit_code == 0
    assert stdout == "+HELLO +WORLD"
    assert stderr == ""


def test_decode_text_argument():
    exit_code, stdout, stderr = run_cli("decode", "+HELLO +WORLD")

    assert exit_code == 0
    assert stdout == "Hello World"
    assert stderr == ""


def test_encode_text_argument_preserves_explicit_trailing_newline():
    exit_code, stdout, stderr = run_cli("encode", "Hello World\n")

    assert exit_code == 0
    assert stdout == "+HELLO +WORLD%0A"
    assert stderr == ""


def test_decode_text_argument_preserves_explicit_trailing_newline():
    exit_code, stdout, stderr = run_cli("decode", "+HELLO +WORLD%0A")

    assert exit_code == 0
    assert stdout == "Hello World\n"
    assert stderr == ""


def test_encode_reads_stdin_when_text_argument_is_omitted():
    exit_code, stdout, stderr = run_cli("encode", stdin="Hello World")

    assert exit_code == 0
    assert stdout == "+HELLO +WORLD"
    assert stderr == ""


def test_decode_reads_stdin_when_text_argument_is_omitted():
    exit_code, stdout, stderr = run_cli("decode", stdin="+HELLO +WORLD")

    assert exit_code == 0
    assert stdout == "Hello World"
    assert stderr == ""


def test_encode_stdin_preserves_single_trailing_newline():
    exit_code, stdout, stderr = run_cli("encode", stdin="Hello World\n")

    assert exit_code == 0
    assert stdout == "+HELLO +WORLD%0A"
    assert stderr == ""


def test_decode_stdin_preserves_single_trailing_newline():
    exit_code, stdout, stderr = run_cli("decode", stdin="+HELLO +WORLD%0A")

    assert exit_code == 0
    assert stdout == "Hello World\n"
    assert stderr == ""


def test_malformed_decode_input_exits_nonzero_and_writes_stderr():
    exit_code, stdout, stderr = run_cli("decode", "+")

    assert exit_code != 0
    assert stdout == ""
    assert "decode error" in stderr
    assert "dangling '+' escape" in stderr


def test_help_includes_examples(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    assert "examples:" in captured.out
    assert 'b45 encode "Hello World"' in captured.out
    assert 'b45 decode "+HELLO +WORLD"' in captured.out
