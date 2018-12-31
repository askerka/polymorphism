from typing import Tuple, Any

from polymorphism import Polymorphism
import pytest  # type: ignore


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


def test_dispatch_only_keyword():
    # noinspection PyMethodMayBeStatic,PyRedeclaration
    class Simple(Polymorphism):
        def calc(self, x: str, y: str, *, cast: type) -> Any:
            raise Exception

        def calc(self, x: str, y: str) -> type:
            return str

    simple = Simple()

    assert simple.calc('1', '2') == str


def test_call_only_positional():
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

    simple = Simple()

    assert simple.calc(1, 2) == (int, int)
    assert simple.calc(1, 2.0) == (int, float)
