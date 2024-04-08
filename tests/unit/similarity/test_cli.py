from click.testing import CliRunner

from dbally_cli.similarity import update_index


def test_cli():
    """
    Test the update_index command with a specific module path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.submodule"])
    assert result.exit_code == 0
    assert "BarView.method_baz.person, FooView.method_bar.year" in result.output
    assert "FooView.method_bar.city, FooView.method_foo.idx" in result.output
    assert "Indexes updated successfully" in result.output


def test_cli_with_view():
    """
    Test the update_index command with a specific module and view path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.submodule:FooView"])
    assert result.exit_code == 0
    assert "FooView.method_bar.year" in result.output
    assert "FooView.method_bar.city, FooView.method_foo.idx" in result.output
    assert "Indexes updated successfully" in result.output


def test_cli_no_indexes():
    """
    Test the update_index command with a module that has no indexes
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.empty_submodule"])
    assert result.exit_code != 0
    assert "No similarity indexes found" in result.output


def test_cli_with_invalid_path():
    """
    Test the update_index command with an invalid path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.invalid_submodule"])
    assert result.exit_code != 0
    assert "Module sample_module.invalid_submodule not found" in result.output


def test_cli_with_invalid_view():
    """
    Test the update_index command with an invalid view path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.submodule:InvalidView"])
    assert result.exit_code != 0
    assert "View InvalidView not found in module sample_module.submodule" in result.output


def test_cli_with_invalid_method():
    """
    Test the update_index command with an invalid method path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.submodule:FooView.invalid_method"])
    assert result.exit_code != 0
    assert "Filter method invalid_method not found in view FooView" in result.output


def test_cli_with_invalid_argument():
    """
    Test the update_index command with an invalid argument path
    """
    runner = CliRunner()
    result = runner.invoke(update_index, ["sample_module.submodule:FooView.method_bar.invalid_argument"])
    assert result.exit_code != 0
    assert "Argument invalid_argument not found in method method_bar" in result.output
