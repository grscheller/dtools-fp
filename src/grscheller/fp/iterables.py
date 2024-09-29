# Copyright 2023-2024 Geoffrey R. Scheller
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

"""
### Library of iterator related functions.

* iterables are not necessarily iterators
* at all times iterator protocol is assumed to be followed, that is
  * all iterators are assumed to be iterable
  * for all iterators `foo` we assume `iter(foo) is foo`

"""
from __future__ import annotations
from enum import auto, Enum
from typing import Callable, cast, Final, Iterator, Iterable
from typing import overload, Optional, Reversible, TypeVar
from .nada import Nada, nada
from .woException import MB

__all__ = [ 'drop', 'dropWhile', 'take', 'takeWhile',
            'concat', 'merge', 'exhaust', 'FM',
            'accumulate', 'foldL', 'foldR', 'foldL_sc', 'foldR_sc' ]

class FM(Enum):
    CONCAT = auto()
    MERGE = auto()
    EXHAUST = auto()

D = TypeVar('D')      # D for Data
L = TypeVar('L')      # L for Left
R = TypeVar('R')      # R for Right
S = TypeVar('S')      # S for Sentinel (also used for default values)
T = TypeVar('T')      # T for sTate

## Iterate over multiple Iterables

def concat(*iterables: Iterable[D]) -> Iterator[D]:
    """Sequentially concatenate multiple iterables together.

    * pure Python version of standard library's itertools.chain
    * iterator sequentially yields each iterable until all are exhausted
    * an infinite iterable will prevent subsequent iterables from yielding any values
    * performant to chain

    """
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value = next(iterator)
                yield value
            except StopIteration:
                break

def exhaust(*iterables: Iterable[D]) -> Iterator[D]:
    """Shuffle together multiple iterables until all are exhausted.

    * iterator yields until all iterables are exhausted

    """
    iterList = list(map(lambda x: iter(x), iterables))
    if (numIters := len(iterList)) > 0:
        ii = 0
        values = []
        while True:
            try:
                while ii < numIters:
                    values.append(next(iterList[ii]))
                    ii += 1
                for value in values:
                    yield value
                ii = 0
                values.clear()
            except StopIteration:
                numIters -= 1
                if numIters < 1:
                    break
                del iterList[ii]
        for value in values:
            yield value

def merge(*iterables: Iterable[D], yield_partials: bool=False) -> Iterator[D]:
    """Shuffle together multiple iterables until one is exhausted.

    * iterator yields until one of the iterables is exhausted
    * if yield_partials is true, yield any unmatched yielded values from other iterables
      * prevents data lose if any of the iterables are iterators with external references

    """
    iterList = list(map(lambda x: iter(x), iterables))
    values = []
    if (numIters := len(iterList)) > 0:
        while True:
            try:
                for ii in range(numIters):
                    values.append(next(iterList[ii]))
                for value in values:
                    yield value
                values.clear()
            except StopIteration:
                break
        if yield_partials:
            for value in values:
                yield value

## dropping and taking

def drop(iterable: Iterable[D], n: int) -> Iterator[D]:
    """Drop the next `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
        except StopIteration:
            break
    return it

def dropWhile(iterable: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]:
    """Drop initial values from `iterable` while predicate is true."""
    it = iter(iterable)
    try:
        value = next(it)
    except:
        return it

    while True:
        try:
            if not pred(value):
                break
            value = next(it)
        except StopIteration:
            break
    return concat((value,), it)

def take(iterable: Iterable[D], n: int) -> Iterator[D]:
    """Take up to `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
            yield value
        except StopIteration:
            break

def takeWhile(iterable: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]:
    """Yield values from `iterable` while predicate is true.

       * potential value loss if iterable is iterator with external references

    """
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            if pred(value):
                yield value
            else:
                break
        except StopIteration:
            break

## reducing and accumulating

def accumulate(iterable: Iterable[D], f: Callable[[L, D], L],
               initial: Optional[L]=None) -> Iterator[L]:
    """
    Returns an iterator of accumulated values.

    * pure Python version of standard library's itertools.accumulate
    * function f does not default to addition (for typing flexibility)
    * begins accumulation with an optional starting value
    * itertools.accumulate had mypy issues

    """
    it = iter(iterable)
    try:
        it0 = next(it)
    except StopIteration:
        if initial is None:
            return
        else:
            yield initial
    else:
        if initial is not None:
            yield initial
            acc = f(initial, it0)
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc
        else:
            acc = cast(L, it0)  # in this case L = D
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc

# @overload
# def foldL(iterable: Iterable[D],
#           f: Callable[[L, D], L],
#           init: L,
#           sent: S) -> L: ...
# @overload
# def foldL(iterable: Iterable[D],
#           f: Callable[[L, D], L],
#           init: L) -> L: ...
# @overload
# def foldL(iterable: Iterable[D],
#           f: Callable[[D, D], D]) -> D|None: ...
# @overload
# def foldL(iterable: Iterable[D],
#           f: Callable[[D, D], D],
#           init: D) -> D: ...
def foldL(iterable: Iterable[D],
          f: Callable[[L, D], L],
          init: Optional[L]=None,
          sent: Optional[S]=None) -> L|S:
    """
    Folds an iterable left with optional initial value.

    * traditional FP type order given for function f
    * note that ~S and ~L can be the same types
      * when an initial value is not given then ~L = ~D
      * if iterable empty & no initial value given, return default
    * never returns if iterable generates an infinite iterator

    """
    it = iter(iterable)
    _init: L = cast(L, init)
    _sent: S = cast(S, sent)

    acc: L

    if _init is None:
        try:
            acc = cast(L, next(it))
        except StopIteration:
            return _sent
    else:
        acc = _init

    for v in it:
        acc = f(acc, v)

    return acc

# @overload
# def foldR(iterable: Reversible[D],
#           f: Callable[[D, R], R],
#           init: R,
#           sent: S) -> R: ...
# @overload
# def foldR(iterable: Reversible[D],
#           f: Callable[[D, R], R],
#           init: R) -> R: ...
# @overload
# def foldR(iterable: Reversible[D],
#           f: Callable[[D, D], D]) -> D|None: ...
# @overload
# def foldR(iterable: Reversible[D],
#           f: Callable[[D, D], D],
#           init: D) -> D: ...
def foldR(iterable: Reversible[D],
          f: Callable[[D, R], R],
          init: Optional[R]=None,
          sent: Optional[S]=None) -> R|S:
    """
    Folds a reversible iterable right with an optional initial value.

    * traditional FP type order given for function f
    * note that ~S and ~R can be the same types
      * if initial value is not given then ~R = ~D
      * if iterable empty & no initial value given, return sentinel value

    """
    it = reversed(iterable)
    _init: R = cast(R, init)
    _sent: S = cast(S, sent)

    acc: R

    if _init is None:
        try:
            acc = cast(R, next(it))
        except StopIteration:
            return _sent
    else:
        acc = _init

    for v in it:
        acc = f(v, acc)

    return acc

# @overload
# def foldL_sc(iterable: Iterable[D|S],
#              f: Callable[[L, D], L],
#              init: L,
#              sent: S,
#              pred: Callable[[D, T], MB[T]],
#              istate: T) -> L: ...
# @overload
# def foldL_sc(iterable: Iterable[D],
#              f: Callable[[L, D], L],
#              init: L,
#              sent: S,
#              pred: Callable[[D, T], MB[T]],
#              istate: T) -> L: ...
# @overload
# def foldL_sc(iterable: Iterable[D],
#              f: Callable[[L, D], L],
#              init: L) -> L: ...
# @overload
# def foldL_sc(iterable: Iterable[D],
#              f: Callable[[D, D], D]) -> D|None: ...
# @overload
# def foldL_sc(iterable: Iterable[D],
#              f: Callable[[D, D], D],
#              init: D) -> D: ...
def foldL_sc(iterable: Iterable[D|S],
             f: Callable[[L, D], L],
             init: Optional[L]=None,
             sent: Optional[S]=None,
             pred: Optional[Callable[[D, T], MB[T]]]=None,
             istate: Optional[T]=None) -> L|S:
    """
    Shortcut version of foldL.

    * stop fold if sentinel value `sent` is encountered
      * if the iterable returns the sentinel value, stop the fold at that point
        * f is never passed the sentinel value
        * predicate `pred` provides a "short circuit" capability
          * the default `pred` does not "short circuit"
            * ignores the data
            * just passes along the initial state `istate` unchanged
    * folding function `f` is never passed the sentinel value

    """
    sentinel = cast(S, sent)
    initial_state = cast(T, istate)
    if pred is None:
        predicate: Callable[[D, T], MB[T]]  = lambda d, t: MB(t)
    else:
        predicate = pred

    it = iter(iterable)
    state_mb = MB(initial_state)

    acc: L

    if init is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return sentinel  # if sentinel defaults to None, we take S to be NoneType
    else:
        acc = init

    for d in it:
        if d is sentinel or d == sentinel:
            break
        else:
            if (state_mb := predicate(cast(D, d), state_mb.get())):
                f_ret = f(acc, cast(D, d))
                acc = f_ret
            else:
                break

    return acc

# @overload
# def foldR_sc(iterable: Iterable[D|S],
#              f: Callable[[D, R], R],
#              init: R,
#              sent: S,
#              pred: Callable[[D, T], MB[T]],
#              istate: T) -> R: ...
# @overload
# def foldR_sc(iterable: Iterable[D],
#              f: Callable[[D, R], R],
#              init: R,
#              sent: S,
#              pred: Callable[[D, T], MB[T]],
#              istate: T) -> R: ...
# @overload
# def foldR_sc(iterable: Iterable[D],
#              f: Callable[[D, R], R],
#              init: R) -> R: ...
# @overload
# def foldR_sc(iterable: Iterable[D],
#              f: Callable[[D, D], D]) -> D|None: ...
# @overload
# def foldR_sc(iterable: Iterable[D],
#              f: Callable[[D, D], D],
#              init: D) -> D: ...
def foldR_sc(iterable: Iterable[D|S],
             f: Callable[[D, R], R],
             init: Optional[R]=None,
             sent: Optional[S]=None,
             pred: Optional[Callable[[D, T], MB[T]]]=None,
             istate: Optional[T]=None) -> R|S:
    """
    Shortcut version of foldR.

    * start fold if sentinel value `sent` is encountered
      * if the iterable returns the sentinel value, start the fold at that point
        * f is never passed the sentinel value
        * predicate `pred` provides a "shortcut circuit" capability
          * the default `pred` does not "short circuit"
            * ignores the data
            * just passes along the initial state `istate` unchanged
    * folding function `f` is never passed the sentinel value
    * does not require iterable to be reversible, iterable never "reversed"
    * does not raise RecursionError, recursion simulated with Python list

    """
    sentinel = cast(S, sent)
    initial_state = cast(T, istate)
    if pred is None:
        predicate: Callable[[D, T], MB[T]]  = lambda d, t: MB(t)
    else:
        predicate = pred

    it = iter(iterable)
    state_mb = MB(initial_state)

    acc: R

    ds: list[D] = []
    for d in it:
        if d is sentinel or d == sentinel:
            break
        else:
            if (state_mb := predicate(cast(D, d), state_mb.get())):
                ds.append(cast(D, d))
            else:
                break

    if init is None:
        if len(ds) == 0:
            return sentinel  # if sentinel defaults to None, we take S to be NoneType
        else:
            acc = cast(R, ds.pop())  # in this case R = D
    else:
        acc = init

    while ds:
        acc = f(ds.pop(), acc)

    return acc
