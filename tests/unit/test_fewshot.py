from typing import Callable, List, Tuple

import pytest

from dbally.prompts.elements import FewShotExample


class TestExamples:
    def studied_at(self, _: str):
        return False

    def is_available_within_months(self, _: int):
        return False

    def data_scientist_position(self):
        return False

    def has_seniority(self, _: str):
        return False

    def __call__(self) -> List[Tuple[str, Callable]]:  # pylint: disable=W0602, C0116, W9011
        return [
            (
                # dummy test
                "None",
                lambda: None,
            ),
            (
                # test lambda
                "True and False or data_scientist_position() or (True or True)",
                lambda: (True and False or self.data_scientist_position() or (True or True)),
            ),
            (
                # test string
                'studied_at("University of Toronto")',
                lambda: self.studied_at("University of Toronto"),
            ),
            (
                # test complex conditions with comments
                'is_available_within_months(1) and data_scientist_position() and has_seniority("senior")',
                lambda: (
                    self.is_available_within_months(1)
                    and self.data_scientist_position()
                    and self.has_seniority("senior")
                ),  # pylint: disable=line-too-long
            ),
            (
                # test nested conditions with comments
                'data_scientist_position(1) and (has_seniority("junior") or has_seniority("senior"))',
                lambda: (
                    self.data_scientist_position(1)
                    and (
                        self.has_seniority("junior") or self.has_seniority("senior")
                    )  # pylint: disable=too-many-function-args
                ),
            ),
        ]


def test_fewshot_string():
    result = FewShotExample("question", "answer")
    assert result.answer == "answer"
    assert str(result) == "answer"


@pytest.mark.parametrize(
    "repr_lambda",
    TestExamples()(),
)
def test_fewshot_lambda(repr_lambda: Tuple[str, Callable]):
    result = FewShotExample("question", repr_lambda[1])
    assert str(result) == repr_lambda[0]
