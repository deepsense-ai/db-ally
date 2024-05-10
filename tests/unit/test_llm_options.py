from dataclasses import dataclass

import pytest
from openai import NOT_GIVEN

from dbally.data_models.llm_options import LLMOptions


@dataclass
class OptionCase:
    frequency_penalty: float
    max_tokens: int


@pytest.mark.parametrize(
    "default_params,input_params,expected_params",
    [
        (OptionCase(0.0, 100), OptionCase(1.1, 200), OptionCase(1.1, 200)),
        (OptionCase(0.0, 100), OptionCase(1.1, None), OptionCase(1.1, None)),
        (OptionCase(0.0, NOT_GIVEN), OptionCase(1.1, 200), OptionCase(1.1, 200)),
        (OptionCase(0.0, 100), OptionCase(0.1, NOT_GIVEN), OptionCase(0.1, 100)),
        (OptionCase(0.0, 100), OptionCase(None, NOT_GIVEN), OptionCase(None, 100)),
    ],
)
def test_llm_options_or_operator(default_params, input_params, expected_params):
    default_options = LLMOptions(**default_params.__dict__)
    input_options = LLMOptions(**input_params.__dict__)
    expected_options = LLMOptions(**expected_params.__dict__)

    result = default_options | input_options

    assert result.frequency_penalty == expected_options.frequency_penalty
    assert result.max_tokens == expected_options.max_tokens
