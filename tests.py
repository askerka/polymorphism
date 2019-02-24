from types import MethodType
from typing import Tuple, Any, Dict

import pytest  # type: ignore

from polymorphism import Polymorphism, overload


def test_overload():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: str, y: str) -> type:
            return str

    simple = Simple()

    assert simple.calc(1, 2) == int
    assert simple.calc('1', '2') == str


def test_internal_dispatch():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

        def calc(self, x: str, y: str, *, cast: type) -> type:
            return self.calc(cast(x), cast(y))

    simple = Simple()

    assert simple.calc('1', '2', cast=float) == float


def test_dispatch_with_only_keyword():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: str, y: str, *, cast: type) -> Any:
            raise Exception

        def calc(self, x: str, y: str) -> type:
            return str

    simple = Simple()

    assert simple.calc('1', '2') == str


def test_call_keyword_arguments():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

    simple = Simple()

    assert simple.calc(x=1, y=2) == int
    assert simple.calc(y=2.0, x=1.0) == float


def test_signature_overlap():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> Tuple[type, type]:
            return int, int

        def calc(self, x: int, y: float) -> Tuple[type, type]:
            return int, float

    assert Simple().calc(1, 2) == (int, int)


def test_using_simple_descriptor():
    # noinspection PyPep8Naming
    class dummy:
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, class_):
            if instance is None:
                return self
            return MethodType(self.func, instance)

    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        @dummy
        def calc(self, x: int, y: int) -> type:
            return int

        @classmethod
        def calc(cls, x: float, y: float) -> type:
            return float

    simple = Simple()

    assert simple.calc(1, 2) == int
    assert simple.calc(1.0, 2.0) == float


def test_complicated_descriptor_with_convention():
    # noinspection PyPep8Naming
    class dummy:
        def __init__(self, func):
            self.__wrapped__ = func

        def __get__(self, instance, class_):
            if instance is None:
                return self
            return MethodType(self, instance)

        def __call__(self, *args, **kwargs):
            return self.__wrapped__(*args, **kwargs)

    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        @dummy
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

    simple = Simple()

    assert simple.calc(1, 2) == int
    assert simple.calc(1.0, 2.0) == float


def test_complicated_descriptor_without_convention():
    # noinspection PyPep8Naming
    class dummy:
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, class_):
            if instance is None:
                return self
            return MethodType(self, instance)

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    with pytest.raises(TypeError, match='__wrapped__'):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            @dummy
            def calc(self, x: int, y: int) -> type:
                return int

            def calc(self, x: float, y: float) -> type:
                return float


def test_data_descriptor_overload():
    with pytest.raises(TypeError, match='shade'):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y: int) -> type:
                return int

            @property
            def calc(self) -> type:
                return float


def test_var_positional_arguments():
    with pytest.raises(TypeError, match='variable length'):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, *y: Tuple[int]) -> type:
                return int

            def calc(self, x: float, y: float) -> type:
                return float


def test_var_keyword_arguments():
    with pytest.raises(TypeError, match='variable length'):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y: int) -> type:
                return int

            def calc(self, x: float, **y: Dict[str, float]) -> type:
                return float


def test_method_without_arguments():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self) -> None:
            return None

    simple = Simple()

    assert simple.calc() is None


def test_instance_method_on_class():
    # noinspection PyPep8Naming
    class dummy:
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, class_):
            if instance is None:
                return self
            return MethodType(self.func, instance)

    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        @dummy
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

    with pytest.raises(TypeError, match='is not callable'):
        # noinspection PyCallByClass
        Simple.calc(1, 2)


def test_class_method_on_instance():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        @classmethod
        def calc(cls, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

    assert Simple().calc(1, 2) == int


def test_class_method_on_class():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> Tuple[type, type]:
            return int, int

        @staticmethod
        def calc(x: int, y: float) -> Tuple[type, type]:
            return int, float

        @classmethod
        def calc(cls, x: int, y: str) -> Tuple[type, type]:
            return int, str

    # noinspection PyCallByClass
    assert Simple.calc(1, y='2') == (int, str)


def test_static_method():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        @staticmethod
        def calc(x: int, y: int) -> type:
            return int

        @staticmethod
        def calc(x: float, y: float) -> type:
            return float

        def calc(self, x: str, y: str) -> type:
            return str

    assert Simple.calc(1.0, 2.0) == float


def test_ambiguous_overload_default_argument():
    with pytest.raises(
            TypeError, match=r'Overloading .* \({0}, {0}\) types'.format(int)
    ):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y: int) -> type:
                return int

            def calc(self, x: int, y: int, z: int = 3) -> type:
                return int


def test_ambiguous_overload_class_method():
    with pytest.raises(
            TypeError, match=r'Overloading .* \({0}, {0}\) types'.format(int)
    ):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y: int) -> type:
                return int

            @classmethod
            def calc(cls, x: int, y: int) -> type:
                return int


def test_ambiguous_overload_static_method():
    with pytest.raises(
            TypeError, match=r'Overloading .* \({0}, {0}\) types'.format(int)
    ):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y: int) -> type:
                return int

            @staticmethod
            def calc(x: int, y: int) -> type:
                return int


def test_class_without_overload():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x, *args, y: int) -> type:
            return int

    simple = Simple()
    # noinspection PyTypeChecker
    assert simple.calc('1', y='2') == int


def test_argument_without_annotation():
    with pytest.raises(
            TypeError, match=r'Argument .* should be annotated'
    ):
        # noinspection PyMethodMayBeStatic,PyRedeclaration
        class Simple(Polymorphism):
            def calc(self, x: int, y) -> type:
                return int

            @staticmethod
            def calc(x: int, y: int) -> type:
                return int


def test_mismatched_call():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> type:
            return int

        def calc(self, x: float, y: float) -> type:
            return float

    with pytest.raises(TypeError, match='not exists'):
        Simple().calc(1, 2.0)


def test_overload_decorator():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple:
        @overload
        def calc(self, x: int, y: int) -> type:
            return int

        @calc.overload
        def calc_str(self, x: str, y: str) -> type:
            return str

        # noinspection PyNestedDecorators
        @calc.overload
        @classmethod
        def calc_float(cls, x: float, y: float) -> type:
            return float

    # noinspection PyCallByClass
    assert Simple.calc(1.0, 2.0) == float
