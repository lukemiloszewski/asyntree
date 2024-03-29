from typer.testing import CliRunner

from asyntree import __main__


def test_main_runs(runner: CliRunner) -> None:
    result = runner.invoke(__main__.app)
    assert result.exit_code == 0
