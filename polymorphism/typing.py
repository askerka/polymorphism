from types import FunctionType, MemberDescriptorType, MethodType
from typing import Union

__all__ = ['AnyMethodType', 'FunctionOrDescriptorType']

FunctionOrDescriptorType = Union[FunctionType, MemberDescriptorType]
AnyMethodType = Union[FunctionType, MemberDescriptorType, MethodType]
