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

"""### Module fp.iterables - Iterator related tools

Library of iterator related functions and enumerations.

* Concatenating and merging iterables
* Dropping and taking values from iterables
* Reducing and accumulating iterables

#### Assumptions
* iterables are not necessarily iterators
* at all times iterator protocol is assumed to be followed, that is
  * all iterators are assumed to be iterable
  * for all iterators `foo` we assume `iter(foo) is foo`

"""
from __future__ import annotations
from collections.abc import Callable, Iterable, Iterator
from enum import auto, Enum
from typing import cast, Never, Protocol
from .err_handling import MB
from .function import negate, swap
from .singletons import NoValue

__all__ = [ 'FM', 'concat', 'merge', 'exhaust',
            'drop', 'drop_while',
            'take', 'take_while',
            'take_split', 'take_while_split',
            'accumulate', 'foldL0', 'foldL1', 'mbFoldL', 'scFoldL', 'scFoldR' ]

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

def drop[D](iterable: Iterable[D], n: int, /) -> Iterator[D]:
    """Drop the next `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            next(it)
        except StopIteration:
            break
    return it

def drop_while[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
    """Drop initial values from `iterable` while predicate is true."""
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            if not pred(value):
                it = concat((value,), it)
                break
        except StopIteration:
            break
    return it

def take[D](iterable: Iterable[D], n: int, /) -> Iterator[D]:
    """Return an iterator of up to `n` initial values of an iterable"""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
            yield value
        except StopIteration:
            break

def take_split[D](iterable: Iterable[D], n: int, /) -> tuple[Iterator[D], Iterator[D]]:
    """Same as take except also return an iterator of the remaining values.

       * return a tuple of
         * an iterator of up to `n` initial values
         * an iterator of the remaining vales of the `iterable`
       * best practice is not to access second iterator until first is exhausted

    """
    it = iter(iterable)
    itn = take(it, n)

    return itn, it

def take_while[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
    """Yield values from `iterable` while predicate is true.

    **Warning:** risk of value loss if iterable is multiple referenced iterator.
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

def take_while_split[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> tuple[Iterator[D], Iterator[D]]:
    """Yield values from `iterable` while `predicate` is true.

       * return a tuple of two iterators
         * first of initial values where predicate is true, followed by first to fail
         * second of the remaining values of the iterable after first failed value
       * best practice is not to access second iterator until first is exhausted

    """
    def _take_while(it: Iterator[D],
                    pred: Callable[[D], bool],
                    val: MB[D]) -> Iterator[D]:
        while True:
            try:
                val.put(next(it))
                if pred(val.get()):
                    yield val.pop()
                else:
                    break
            except StopIteration:
                break

    it = iter(iterable)
    value: MB[D] = MB()
    it_pred = _take_while(it, pred, value)

    return (it_pred, concat(value, it))

## reducing and accumulating

def accumulate[D,L](iterable: Iterable[D], f: Callable[[L, D], L], initial: L|NoValue=NoValue(), /) -> Iterator[L]:
    """Returns an iterator of accumulated values.

    * pure Python version of standard library's `itertools.accumulate`
    * function `f` does not default to addition (for typing flexibility)
    * begins accumulation with an optional `initial` value

    """
    it = iter(iterable)
    try:
        it0 = next(it)
    except StopIteration:
        if initial is NoValue():
            return
        else:
            yield cast(L, initial)
    else:
        if initial is not NoValue():
            init = cast(L, initial)
            yield init
            acc = f(init, it0)
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

def reduceL[D](iterable: Iterable[D], f: Callable[[D, D], D], /) -> D|Never:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
    * if iterable empty raises StopIteration exception
    * does not catch any exception `f` raises
    * never returns if `iterable` generates an infinite iterator

    """
    it = iter(iterable)
    try:
        acc = next(it)
    except StopIteration:
        msg = "Attemped to left fold an empty iterable."
        raise StopIteration(msg)

    for v in it:
        acc = f(acc, v)

    return acc

def foldL[D, L](iterable: Iterable[D], f: Callable[[L, D], L], initial: L, /) -> L|Never:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
    * does not catch any exception `f` may raise
    * like builtin `sum` for Python >=3.8 except
      - not restricted to __add__ for the folding function
      - initial value required, does not default to `0` for initial value
      - handles non-numeric data just find
    * never returns if `iterable` generates an infinite iterator

    """
    acc = initial
    for v in iterable:
        acc = f(acc, v)
    return acc

def mbFoldL[L, D](
        iterable: Iterable[D],
        f: Callable[[L, D], L],
        initial: L|NoValue=NoValue()
    ) -> MB[L]:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
    * when an initial value is not given then `~L = ~D`
    * if iterable empty and no `initial` value given, return `MB()`
    * never returns if iterable generates an infinite iterator

    """
    acc: L
    it = iter(iterable)
    if initial is NoValue():
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return MB()
    else:
        acc = cast(L, initial)

    for v in it:
        try:
            acc = f(acc, v)
        except Exception:
            return MB()

    return MB(acc)

def scReduceL[D](
        iterable: Iterable[D],
        f: Callable[[D, D], D], /,
        start: Callable[[D], bool]=(lambda d: True),
        stop: Callable[[D], bool]=(lambda d: False),
        include_start: bool=True,
        include_stop: bool=True
    ) -> tuple[D, Iterable[D]]:
    """Short circuit version of a left reduce. Useful for infinite or
     non-reversible iterables.

    * Behavior for default arguments will
      * left fold finite iterable
      * start folding immediately
      * continue folding until end (of a possibly infinite iterable)
    * Callable `start` delays starting the left fold
    * Callable `stop` prematurely stop the left

    """
    it1 = drop_while(iterable, negate(start))
    it2, it3 = take_while_split(it1, negate(stop))
    if include_start:
        pass
    else:
        try:
            next(it2)
        except StopIteration:
            pass

    if include_stop:
        reduced = reduceL(it2, f)
        try:
            reduced = f(reduced, next(it3))
        except StopIteration:
            pass
        return (reduced, it3)
    else:
        return (reduceL(it2, f), it3)

def scReduceR[D](
        iterable: Iterable[D],
        f: Callable[[D, D], D], /,
        start: Callable[[D], bool]=(lambda d: False),
        stop: Callable[[D], bool]=(lambda d: False),
        include_start: bool=True,
        include_stop: bool=True
    ) -> tuple[D, Iterable[D]]:
    """Short circuit version of a right reduce. Useful for infinite or
    non-reversible iterables.

    * Behavior for default arguments will
      * right fold finite iterable
      * start folding at end (of a possibly infinite iterable)
      * continue folding right until beginning
    * Callable `start` prematurely starts the right fold
    * Callable `stop` prematurely stops the right fold
    * best practice is not to access second iterator until first is exhausted

    """
    it1, it2 = take_while_split(iterable, negate(start))
    l1 = list(it1)
    if include_start:
        try:
            begin = next(it2)
        except StopIteration:
            pass
        else:
            l1.append(begin)

    l1.reverse()
    it3, it4 = take_while_split(l1, negate(stop))

    reduced = reduceL(it3, swap(f))
    if include_stop:
        try:
            end = next(it4)
        except StopIteration:
            pass
        else:
            reduced = f(end, reduced)

    return (reduced, it2)

