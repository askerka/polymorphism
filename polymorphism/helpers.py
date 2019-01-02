from inspect import ismethoddescriptor, isfunction, isclass
from types import MethodType, MemberDescriptorType, FunctionType
from typing import cast, Any

from .typing import AnyMethodType

__all__ = ['is_overridable', 'sanitize_method']


def is_overridable(obj) -> bool:
    return ismethoddescriptor(obj) or isfunction(obj)


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

    # Something goes wrong, should never happen
    raise RuntimeError
