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

"""### Module fp.iterables - Iterator related tools

Library of iterator related functions and enumerations.

* iterables are not necessarily iterators
* at all times iterator protocol is assumed to be followed, that is
  * all iterators are assumed to be iterable
  * for all iterators `foo` we assume `iter(foo) is foo`

#### Concatenating and merging iterables:

* **function concat:** sequentially chain iterables
* **function exhaust:** shuffle together iterables until all are exhausted
* **function merge:** shuffle together iterables until one is exhausted

---

#### Dropping and taking values from an iterable:

* **function drop:** drop first `n` values from iterable
* **function dropWhile:** drop values from iterable while predicate holds
* **function take:** take up to `n` initial values from iterable
* **function takeWhile:** take values from iterable while predicate holds

---

#### Reducing and accumulating an iterable:

* **function accumulate:** take iterable & function, return iterator of accumulated values
* **function foldL:** fold iterable from the left with a function
* **function foldR:** fold reversible iterable from the right with a function
* **function foldLsc:** fold iterable from left with function and a premature stop condition
* **function foldRsc:** fold iterable from right with function and a premature start condition

---

#### Iterator related utility functions

* **function itargs:** function reterning an iterator of its arguments

---

"""
from __future__ import annotations
from collections.abc import Callable, Iterator, Iterable, Reversible
from enum import auto, Enum
from typing import cast
from .err_handling import MB

__all__ = [ 'FM', 'concat', 'merge', 'exhaust',
            'drop', 'dropWhile', 'take', 'takeWhile',
            'accumulate', 'foldL', 'foldR', 'foldLsc', 'foldRsc',
            'itargs' ]

## Iterate over multiple Iterables

class FM(Enum):
    CONCAT = auto()
    MERGE = auto()
    EXHAUST = auto()

def concat[D](*iterables: Iterable[D]) -> Iterator[D]:
    """Sequentially concatenate multiple iterables together.

    * pure Python version of standard library's `itertools.chain`
    * iterator sequentially yields each iterable until all are exhausted
    * an infinite iterable will prevent subsequent iterables from yielding any values
    * performant to `itertools.chain`

    """
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value = next(iterator)
                yield value
            except StopIteration:
                break

def exhaust[D](*iterables: Iterable[D]) -> Iterator[D]:
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

def merge[D](*iterables: Iterable[D], yield_partials: bool=False) -> Iterator[D]:
    """Shuffle together the `iterables` until one is exhausted.

    * iterator yields until one of the iterables is exhausted
    * if `yield_partials` is true,
      * yield any unmatched yielded values from other iterables
      * prevents data lose
        * if any of the iterables are iterators with external references

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

def drop[D](iterable: Iterable[D], n: int) -> Iterator[D]:
    """Drop the next `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
        except StopIteration:
            break
    return it

def dropWhile[D](iterable: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]:
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

def take[D](iterable: Iterable[D], n: int) -> Iterator[D]:
    """Take up to `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
            yield value
        except StopIteration:
            break

def takeWhile[D](iterable: Iterable[D], pred: Callable[[D], bool]) -> Iterator[D]:
    """Yield values from `iterable` while predicate is true.

    **Warning**, potential value loss if iterable is iterator with multiple
    references.
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

def accumulate[D,L](iterable: Iterable[D], f: Callable[[L, D], L],
                  initial: L|None=None) -> Iterator[L]:
    """Returns an iterator of accumulated values.

    * pure Python version of standard library's `itertools.accumulate`
    * function `f` does not default to addition (for typing flexibility)
    * begins accumulation with an optional `initial` value
    * `itertools.accumulate` had mypy issues

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

def foldL[D,L](iterable: Iterable[D],
          f: Callable[[L, D], L],
          initial: L|None=None) -> MB[L]:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
    * when an initial value is not given then `~L = ~D`
    * if iterable empty and no `initial` value given, return empty `MB()`
    * never returns if `iterable` generates an infinite iterator

    """
    acc: L
    it = iter(iterable)

    if initial is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return MB()
    else:
        acc = initial

    for v in it:
        acc = f(acc, v)

    return MB(acc)

def foldR[D,R](iterable: Reversible[D],
          f: Callable[[D, R], R],
          initial: R|None=None) -> MB[R]:
    """Folds a reversible `iterable` right with an optional `initial` value.

    * `iterable` needs to be reversible
    * traditional FP type order given for function `f`
    * when initial value is not given then `~R = ~D`
    * if iterable empty and no `initial` value given, return an empty `MB()`

    """
    acc: R
    it = reversed(iterable)

    if initial is None:
        try:
            acc = cast(R, next(it))  # in this case R = D
        except StopIteration:
            return MB()
    else:
        acc = initial

    for v in it:
        acc = f(v, acc)

    return MB(acc)

def foldLsc[D,L,S](iterable: Iterable[D],
            f: Callable[[L, D], L],
            initial: L|None=None,
            stopfold: Callable[[D, S], MB[S]]=lambda d, s: MB(s),
            istate: S|None=None) -> MB[L]:
    """Short circuit version of foldL.

    * Callable `stopfold` purpose is to prematurely stop the fold before end
      * useful for infinite iterables

    """
    state = cast(MB[S], MB(istate))

    it = iter(iterable)

    if initial is None:
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return MB()
    else:
        acc = initial

    for d in it:
        if (state := stopfold(d, state.get())):
            acc = f(acc, d)
        else:
            break

    return MB(acc)

def foldRsc[D,R,S](iterable: Iterable[D],
            f: Callable[[D, R], R],
            initial: R|None=None,
            startfold: Callable[[D, S], MB[S]]=lambda d, s: MB(s),
            istate: S|None=None) -> MB[R]:
    """Short circuit version of foldR.

    * Callable `startfold` purpose is to start fold before reaching the end
      * does NOT start fold at end and prematurely stop
      * useful for infinite and non-reversible iterables

    """
    state = cast(MB[S], MB(istate))

    it = iter(iterable)

    acc: R

    ds: list[D] = []
    for d in it:
        if (state := startfold(d, state.get())):
            ds.append(d)
        else:
            break

    if initial is None:
        if len(ds) == 0:
            return MB()
        else:
            acc = cast(R, ds.pop())  # in this case R = D
    else:
        acc = initial

    while ds:
        acc = f(ds.pop(), acc)

    return MB(acc)

## Iterator related utility functions
# TODO: move to fp.experimental.args

def itargs[A](*args: A) -> Iterator[A]:
    """Function returning an iterators of its arguments.

    Useful when an API only provides a constructor taking a single iterable.
    """
    for arg in args:
        yield arg

