from unittest.mock import call, patch

import pytest
from dbally_benchmark.evaluate import evaluate
from omegaconf import DictConfig


@patch("dbally_benchmark.evaluate.e2e_evaluate")
@patch("dbally_benchmark.evaluate.text2sql_evaluate")
@patch("dbally_benchmark.evaluate.iql_evaluate")
@pytest.mark.asyncio
async def test_evaluate(iql_mock, text2sql_mock, e2e_mock) -> None:
    cfg = DictConfig(
        {
            "e2e": {"dataset1": {"key1": "value1"}, "dataset2": {"key2": "value2"}},
            "text2sql": {"dataset3": {"key3": "value3"}},
            "common_key": "common_value",
        }
    )
    await evaluate(cfg)

    e2e_mock.assert_has_calls(
        [call({"key1": "value1", "common_key": "common_value"}), call({"key2": "value2", "common_key": "common_value"})]
    )
    text2sql_mock.assert_has_calls([call({"key3": "value3", "common_key": "common_value"})])
    iql_mock.assert_not_called()
