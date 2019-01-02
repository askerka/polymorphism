Ad hoc polymorphism for Python classes!
=====================================================

Installation
------------
::

    pip install polymorphism

polymorphism support python 3.4+

Usage
-----
To use the ``polymorphism`` simply inherit from the ``Polymorphism`` class::

    from polymorphism import Polymorphism


    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> None:
            pass

        def calc(self, x: float, y: float) -> None:
            pass

Or use it as metaclass::

    from polymorphism import PolymorphismMeta

    class Simple(metaclass=PolymorphismMeta):
        ...


Sometimes adding another class to the inheritance is undesirable, then you can use the ``overload`` decorator::

    from polymorphism import overload


    class Simple(Polymorphism):
        @overload
        def calc(self, x: int, y: int) -> None:
            pass

        @calc.overload
        def calc(self, x: float, y: float) -> None:
            pass

The only difference between using a decorator and inheriting it is checking for method shading. With ``overload`` the next example will not raise exception::

    from polymorphism import overload


    class Simple(Polymorphism):
        @overload
        def calc(self, x: int, y: int) -> None:
            pass

        calc = 5

And ``calc`` would be only the attribute.

Why?
----
The idea to implement polymorphism is not new. Many libraries `implement <https://github.com/mrocklin/multipledispatch>`_ this idea. Even the `standard library <http://docs.python.org/3.4/library/functools.html#functools.singledispatch>`_ has an implementation.

But they do not support use with classes or standard type annotation.

The basic idea of the implementation was inspired by the great book `Python Cookbook 3rd Edition <http://shop.oreilly.com/product/0636920027072.do>`_ by David Beazley and Brian K. Jones. But the implementation in the book did not support usage of keyword arguments!

Advantages
----------
In addition to named arguments the library allows:

* Use standard and custom descriptors
* Use naming (keyword) arguments
* Checks for:

  * Arguments for variable length
  * Missed argument annotation
  * Name of wrapped function of descriptor
  * Shading method by attribute or data descriptor (like ``property``)
  * Redefining the method with the same types

* Using any name for instance, not only ``self``

For all check is raised ``TypeError`` exception.

Limitations
-----------

* Simple types for dispatching
* ``overload`` should be top of decorators
* Custom descriptor should save wrapped function  under "__wrapped__" name
* Obvious, method argument can't be variable length (\* and \*\*)


Examples
--------
There are no restrictions on the use of the number of decorators, you only need to comply the naming convention.

For example::

    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> None:
            pass

        @classmethod
        def calc(cls, x: float, y: float) -> None:
            pass

        @staticmethod
        def calc(x: str, y: str) -> None:
            pass

    Simple().calc(1.0, y=2.0)

While use ``overload`` decorator place it on top::

    class Simple:
        @overload
        def calc(self, x: int, y: int) -> None:
            pass

        @calc.overload
        @classmethod
        def calc_float(cls, x: float, y: float) -> None:
            pass

        @calc.overload
        @staticmethod
        def calc_str(x: str, y: str) -> None:
            pass

With ``overload`` only first method name matter. Other methods can have any other names.

polymorphism checks the class at the time of creation::

    class Simple(Polymorphism):
        def calc(self, x: int, y: int) -> None:
            pass

        def calc(self, x: int, y: int, z: int = 3) -> None:
            pass

The below example will raise ``TypeError`` exception because ``calc`` method overloaded with ``z`` parameter with default value and it is impossible distinct last method from first.

``polymorphism`` will raise ``TypeError`` exception on any wrong overloading, so you don't need worry about correctness of it.

See more examples in `tests.py <https://github.com/asduj/polymorphism/blob/master/tests.py>`_.

To-do
-----

* Complex types for dispatching like ``List[int]``