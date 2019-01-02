from collections import UserDict

__all__ = ['OneTimeSetDict']


class OneTimeSetDict(UserDict):
    def __setitem__(self, key, value):
        if key in self:
            raise TypeError(
                'Overloading an existing method with {} types'.format(key)
            )
        return super().__setitem__(key, value)
