from collections import UserDict
from inspect import (
    Parameter, isclass, isfunction, ismethoddescriptor, signature
)
from operator import attrgetter
from types import FunctionType, MemberDescriptorType, MethodType
from typing import cast, Any, Dict, List, Union

__all__ = ['overload', 'Polymorphism', 'PolymorphismMeta']

FunctionOrDescriptorType = Union[FunctionType, MemberDescriptorType]
AnyMethodType = Union[FunctionType, MemberDescriptorType, MethodType]


def sanitize_method(
        method: AnyMethodType,
        instance: Any = object
) -> MethodType:
    if ismethoddescriptor(method):
        descriptor = cast(MemberDescriptorType, method)
        if not isclass(instance):
            return descriptor.__get__(instance, type(instance))
        else:
            return descriptor.__get__(None, instance)

    elif isfunction(method) and not isclass(instance):
        function = cast(FunctionType, method)
        return MethodType(function, instance)

    raise RuntimeError


class SingleDict(UserDict):
    def __setitem__(self, key, value):
        if key in self:
            raise TypeError(
                'Overloading an existing method with {} types'.format(key)
            )
        return super().__setitem__(key, value)


class MultiMethod:
    def __init__(self, method: FunctionOrDescriptorType) -> None:
        self._methods = cast(
            dict, SingleDict()
        )  # type: Dict[tuple, FunctionOrDescriptorType]
        self.overload(method)

    def overload(self, method: FunctionOrDescriptorType) -> 'MultiMethod':
        types = []  # type: List[type]
        actual_method = sanitize_method(method, object())

        try:
            sig = signature(actual_method)
        except ValueError:
            raise TypeError(
                'Descriptor should save wrapped '
                'function  under "__wrapped__" name'
            )

        for param in sig.parameters.values():
            if param.annotation is Parameter.empty:
                raise TypeError(
                    'Argument "{}" should be annotated'.format(param)
                )

            if param.kind in {Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL}:
                raise TypeError(
                    'Argument "{}" shouldn\'t be variable length'.format(param)
                )

            if param.default is not Parameter.empty:
                self._methods[tuple(types)] = method

            types.append(param.annotation)

        self._methods[tuple(types)] = method

        return self

    def __get__(self, instance, class_=None) -> MethodType:
        if instance is not None:
            return MethodType(self, instance)
        else:
            return MethodType(self, class_)

    def __call__(self, instance: Any, *args, **kwargs) -> Any:
        call_types = tuple(map(type, args))

        if kwargs:
            call_size = len(args) + len(kwargs)
            possible_types = filter(
                lambda t: len(t) == call_size, self._methods.keys()
            )

            if args:
                possible_types = filter(
                    lambda t: t[:len(args)] == call_types, possible_types
                )

            methods = ((t, self._methods[t]) for t in possible_types)

            for types, method in methods:
                # Class object can be passed only to descriptor
                if isclass(instance) and not ismethoddescriptor(method):
                    continue

                actual_method = sanitize_method(method, instance)
                sig = signature(actual_method)

                arguments = sig.bind(*args, **kwargs).arguments

                actual_types = list(map(type, arguments.values()))
                sig_types = list(
                    map(attrgetter('annotation'), sig.parameters.values())
                )

                if actual_types == sig_types:
                    return actual_method(**arguments)

        elif self._methods.get(call_types):
            method = self._methods[call_types]
            actual_method = sanitize_method(method, instance)
            return actual_method(*args, **kwargs)

        call_types = call_types + tuple(map(type, kwargs.values()))
        raise TypeError('Method for types {} not exists'.format(call_types))


def is_overridable(obj) -> bool:
    return ismethoddescriptor(obj) or isfunction(obj)


class MultiDict(UserDict):
    def __setitem__(self, key: str, item: Any) -> None:
        if self.get(key) is None or not is_overridable(self.get(key)):
            return super().__setitem__(key, item)

        if not is_overridable(item):
            raise TypeError

        method = self[key]
        if not isinstance(method, MultiMethod):
            method = MultiMethod(method)
            super().__setitem__(key, method)

        method.overload(item)


class PolymorphismMeta(type):
    def __new__(mcs, name, bases, dict_):
        return type.__new__(mcs, name, bases, dict(dict_))

    @classmethod
    def __prepare__(mcs, name, bases):
        return MultiDict()


class Polymorphism(metaclass=PolymorphismMeta):
    pass


overload = MultiMethod
