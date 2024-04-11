import pytest
from sample_module import submodule

from dbally.similarity.detector import SimilarityIndexDetector, SimilarityIndexDetectorException


def test_detector_with_module():
    """
    Test the SimilarityIndexDetector class with a specific module object
    """
    detector = SimilarityIndexDetector(submodule)
    assert detector.list_views() == [submodule.BarView, submodule.FooView]
    assert detector.list_indexes() == {
        submodule.index_bar: ["BarView.method_baz.person", "FooView.method_bar.year"],
        submodule.index_foo: ["FooView.method_bar.city", "FooView.method_foo.idx"],
    }


def test_detector_with_view():
    """
    Test the SimilarityIndexDetector class with a specific view object
    """
    detector = SimilarityIndexDetector(submodule)
    assert detector.list_indexes(view=submodule.FooView) == {
        submodule.index_bar: ["FooView.method_bar.year"],
        submodule.index_foo: ["FooView.method_bar.city", "FooView.method_foo.idx"],
    }


def test_detectior_with_module_path():
    """
    Test the SimilarityIndexDetector class with a module path
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule")
    assert detector.list_views() == [submodule.BarView, submodule.FooView]
    assert detector.list_indexes() == {
        submodule.index_bar: ["BarView.method_baz.person", "FooView.method_bar.year"],
        submodule.index_foo: ["FooView.method_bar.city", "FooView.method_foo.idx"],
    }


def test_detector_with_module_view_path():
    """
    Test the SimilarityIndexDetector class with a module and view path
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:FooView")
    assert detector.list_views() == [submodule.FooView]
    assert detector.list_indexes() == {
        submodule.index_bar: ["FooView.method_bar.year"],
        submodule.index_foo: ["FooView.method_bar.city", "FooView.method_foo.idx"],
    }


def test_detector_with_module_view_method_path():
    """
    Test the SimilarityIndexDetector class with a module, view, and method path
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:FooView.method_bar")
    assert detector.list_views() == [submodule.FooView]
    assert detector.list_indexes() == {
        submodule.index_bar: ["FooView.method_bar.year"],
        submodule.index_foo: ["FooView.method_bar.city"],
    }


def test_detector_with_module_view_method_argument_path():
    """
    Test the SimilarityIndexDetector class with a module, view, method, and argument path
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:FooView.method_bar.city")
    assert detector.list_views() == [submodule.FooView]
    assert detector.list_indexes() == {submodule.index_foo: ["FooView.method_bar.city"]}


def test_detector_with_module_not_found():
    """
    Test the SimilarityIndexDetector class with a module that does not exist
    """
    with pytest.raises(SimilarityIndexDetectorException) as exc:
        SimilarityIndexDetector.from_path("not_found")
    assert exc.value.message == "Module not_found not found."


def test_detector_with_empty_module():
    """
    Test the SimilarityIndexDetector class with an empty module
    """
    detector = SimilarityIndexDetector.from_path("sample_module.empty_submodule")
    assert detector.list_views() == []
    assert not detector.list_indexes()


def test_detector_with_view_not_found():
    """
    Test the SimilarityIndexDetector class with a view that does not exist
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:NotFoundView")
    with pytest.raises(SimilarityIndexDetectorException) as exc:
        detector.list_views()
    assert exc.value.message == "View NotFoundView not found in module sample_module.submodule."


def test_detector_with_method_not_found():
    """
    Test the SimilarityIndexDetector class with a method that does not exist
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:FooView.not_found")
    with pytest.raises(SimilarityIndexDetectorException) as exc:
        detector.list_indexes()
    assert exc.value.message == "Filter method not_found not found in view FooView."


def test_detector_with_argument_not_found():
    """
    Test the SimilarityIndexDetector class with an argument that does not exist
    """
    detector = SimilarityIndexDetector.from_path("sample_module.submodule:FooView.method_bar.not_found")
    with pytest.raises(SimilarityIndexDetectorException) as exc:
        detector.list_indexes()
    assert exc.value.message == "Argument not_found not found in method method_bar."
