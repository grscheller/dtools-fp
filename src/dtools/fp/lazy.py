# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""### Module fp.lazy - lazy function evaluation

Delayed function evaluations, if needed, usually in some inner scope. FP tools
for "non-strict" function evaluations.

#### Non-strict delayed function evaluation:

* class **Lazy:** Delay evaluation of function taking & returning single values
* function **lazy:** Delay evaluation of a function taking more than one value

"""
from __future__ import annotations

__all__ = [ 'Lazy', 'lazy' ]

from collections.abc import Callable
from typing import Final
from .err_handling import MB, XOR
from .function import sequenced

class Lazy[D, R]():
    """Delayed evaluation of a function mapping a value of type D

    Class instance delays the executable of a function where `Lazy(f, arg)`
    constructs an object that can evaluate the Callable `f` with its argument
    at a later time.

    * first argument `f` taking values of type `~D` to values of type `~R`
    * second argument `arg: ~D` is the argument to be passed to `f`
      * where the type `~D` is the `tuple` type of the argument types to `f`
    * function is evaluated when the eval method is called
    * result is cached unless `pure` is set to `False` in `__init__` method

    Usually use case is to make a function "non-strict" by passing some of its
    arguments wrapped in Lazy instances.
    """
    __slots__ = '_f', '_d', '_result', '_pure'

    def __init__(self, f: Callable[[D], R], d: D, pure: bool=True) -> None:
        self._f: Final[Callable[[D], R]] = f
        self._d: Final[D] = d
        self._pure: Final[bool] = pure
        self._result: XOR[R, MB[Exception]] = XOR(MB(), MB())

    def __bool__(self) -> bool:
        return True if self._result else False

    def is_evaluated(self) -> bool:
        return self._result != XOR(MB(), MB())

    def is_exceptional(self) -> bool:
        if self.is_evaluated():
            return False if self._result else True
        else:
            return False

    def is_pure(self) -> bool:
        return self._pure

    def eval(self) -> bool:
        """Evaluate function with its argument.

        * evaluate function
        * cache results or exceptions if `pure == True`
        * reevaluate if `pure == False`

        """
        if not self.is_evaluated() or not self._pure:
            try:
                result = self._f(self._d)
            except Exception as exc:
                self._result = XOR(MB(), MB(exc))
                return False
            else:
                self._result = XOR(MB(result), MB())
                return True
        if self:
            return True
        else:
            return False

    def result(self) -> MB[R]:
        if not self.is_evaluated():
            self.eval()

        if self._result:
            return MB(self._result.getLeft())
        else:
            return MB()

    def exception(self) -> MB[Exception]:
        if not self.is_evaluated():
            self.eval()
        return self._result.getRight()

def lazy[R, **P](f: Callable[P, R], *args: P.args, pure: bool=True) -> Lazy[tuple[P.args], R]:
    """Delayed evaluation of a function with arbitrary positional arguments.

    Function returning a delayed evaluation of a function of an arbitrary number
    of positional arguments.

    * first positional argument `f` takes a function
    * next positional arguments are the arguments to be applied later to `f`
      * `f` is evaluated when the `eval` method of the returned Lazy is called
      * `f` is evaluated only once with results cached unless `pure` is `False`
      * if `pure` is false, the arguments are reapplied to `f`
        * useful for repeating side effects
        * when arguments are or contain shared references

    """
    return Lazy(sequenced(f), args, pure=pure)

