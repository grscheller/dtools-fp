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

* iterables are not necessarily iterators
* at all times iterator protocol is assumed to be followed, that is
  * all iterators are assumed to be iterable
  * for all iterators `foo` we assume `iter(foo) is foo`

#### Concatenating and merging iterables:

* function **concat**: sequentially chain iterables
* function **exhaust**: shuffle together iterables until all are exhausted
* function **merge**: shuffle together iterables until one is exhausted

---

#### Dropping and taking values from an iterable:

* function **drop**: drop first `n` values from iterable
* function **drop_while**: drop values from iterable while predicate holds
* function **take**: take up to `n` initial values from iterable
* function **take_split**: splitting out initial `n` initial values of iterable * function **take_while**: take values from iterable while predicate holds
* function **take_while_split**: splitting an iterable while predicate holds

---

#### Reducing and accumulating an iterable:

* function **accumulate**: take iterable & function, return iterator of accumulated values
* function **foldL0**: fold iterable left with a function
  * raises `StopIteration` exception if iterable is empty
* function **foldL1**: fold iterable left with a function and initial value
* function **mbFoldL**: fold iterable left with an optional initial value
  * wraps result in a `MB` monad

"""
from __future__ import annotations
from collections.abc import Callable, Iterator, Iterable, Reversible
from enum import auto, Enum
from typing import cast, Never
from grscheller.circular_array.ca import ca
from .err_handling import MB
from .function import swap
from .singletons import NoValue

__all__ = [ 'FM', 'concat', 'merge', 'exhaust',
            'drop', 'drop_while',
            'take', 'take_while',
            'take_pass', 'take_while_pass',
            'accumulate', 'foldL0', 'foldL1', 'mbFoldL' ] #,
            # 'scFoldL', 'scFoldR' ]

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

def drop_while[D](iterable: Iterable[D], predicate: Callable[[D], bool], /) -> Iterator[D]:
    """Drop initial values from `iterable` while predicate is true."""
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            if not predicate(value):
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

    **Warning:** risk of potential value loss if iterable is iterator with
    multiple references.
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

def take_while_split[D](iterable: Iterable[D],
                        predicate: Callable[[D], bool],
                        /) -> tuple[Iterator[D], Iterator[D]]:
    """Yield values from `iterable` while `predicate` is true.

       * return a tuple of two iterators
         * first of initial values where predicate is true, followed by first to fail
         * second of the remaining values of the iterable after first failed value
       * best practice is not to access second iterator until first is exhausted

    """
    def _take_while(it: Iterator[D], pred: Callable[[D], bool], val: list[D]) -> Iterator[D]:
        while True:
            try:
                if val:
                    val[0] = next(it)
                else:
                    val.append(next(it))
                if pred(val[0]):
                    yield val[0]
                    val.pop()
                else:
                    break
            except StopIteration:
                break

    it = iter(iterable)
    value: list[D] = []
    it_pred = _take_while(it, predicate, value)

    return (it_pred, concat(cast(list[D], value), it))

## reducing and accumulating

def accumulate[D,L](iterable: Iterable[D],
                    f: Callable[[L, D], L],
                    initial: L|NoValue=NoValue(), /) -> Iterator[L]:
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

def foldL0[D](iterable: Iterable[D], f: Callable[[D, D], D], /) -> D|Never:
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

def foldL1[D, L](iterable: Iterable[D],
                 f: Callable[[L, D], L],
                 initial: L, /) -> L|Never:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
    * does not catch any exception `f` raises
    * never returns if `iterable` generates an infinite iterator

    """
    acc = initial
    for v in iterable:
        acc = f(acc, v)
    return acc

def mbFoldL[L, D](iterable: Iterable[D],
                  f: Callable[[L, D], L],
                  initial: L|NoValue=NoValue()) -> MB[L]:
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

#def scFoldL[D, L](iterable: Iterable[D],
#                  f: Callable[[L, D], L],
#                  initial: L|NoValue=NoValue(), /,
#                  start_folding: Callable[[D], bool]=lambda d: True,
#                  stop_folding: Callable[[D], bool]=lambda d: False,
#                  include_start: bool=True,
#                  propagate_failed: bool=True) -> tuple[MB[L], Iterable[D]]:
#    """Short circuit version of a left fold. Useful for infinite or
#    non-reversible iterables.
#
#    * Behavior for default arguments will
#      * left fold finite iterable
#      * start folding immediately
#      * continue folding until end (of a possibly infinite iterable)
#    * Callable `start_folding` delays starting a left fold
#    * Callable `stop_folding` is to prematurely stop the folding left
#    * Returns an XOR of either the folded value or error string
#
#    """
#    it = dropWhile(iter(iterable), lambda d: not start_folding(d))
#    if not include_start:
#        it = drop(it, 1)
#    taken2, rest = takeWhile2(it, lambda d: not stop_folding(d))
#    data: ca[D] = ca(taken2)
#    failMB: MB[D] = MB()
#    if data:
#        failMB = MB(data.popR())
#        if propagate_failed:
#            rest = concat((failMB.get()), rest)
#
#
#
#
#    data2 = ca(taken2)
#    data: ca[D] = ca()
#    failMB: MB[D] = MB()
#    for d in data2:
#        if stop_folding(d):
#            if not include_start:
#                failMB = MB(data.popL())
#            if include_stop:
#                data.pushR(d)
#            break
#        else:
#            data.pushL(d)
#
#    return (mbFoldL(taken, f, initial), rest)
#
#def scFoldR[D, R](iterable: Iterable[D],
#                  f: Callable[[D, R], R],
#                  initial: R|NoValue=NoValue(), /,
#                  start_folding: Callable[[D], bool]=lambda d: False,
#                  stop_folding: Callable[[D], bool]=lambda d: False,
#                  include_start: bool=True,
#                  include_stop: bool=True) -> tuple[MB[R], Iterable[D]]:
#    """Short circuit version of a right fold. Useful for infinite or
#    non-reversible iterables.
#
#    * Behavior for default arguments will
#      * right fold finite iterable
#      * start folding at end (of a possibly infinite iterable)
#      * continue folding right until beginning
#    * Callable `start_folding` prematurely starts a right fold
#    * Callable `stop_folding` is to prematurely stops a right fold
#    * Returns an XOR of either the folded value or error string
#    * best practice is not to access second iterator until first is exhausted
#
#    """
#    taken2, rest = takeWhile2(iter(iterable), lambda d: not start_folding(d))
#    data2 = ca(taken2)
#    data: ca[D] = ca()
#    failMB: MB[D] = MB()
#    for d in reversed(data2):
#        if stop_folding(d):
#            if not include_start:
#                failMB = MB(data.popL())
#            if include_stop:
#                data.pushR(d)
#            break
#        else:
#            data.pushL(d)
#
#    if failMB:
#        return (mbFoldL(data, swap(f), initial), concat((failMB.get(),), rest))
#    else:
#        return (mbFoldL(data, swap(f), initial), rest)
#
