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

* function **concat**: sequentially chain iterables
* function **exhaust**: shuffle together iterables until all are exhausted
* function **merge**: shuffle together iterables until one is exhausted

---

#### Dropping and taking values from an iterable:

* function **drop**: drop first `n` values from iterable
* function **dropWhile**: drop values from iterable while predicate holds
* function **take**: take up to `n` initial values from iterable
* function **takeWhile**: take values from iterable while predicate holds

---

#### Reducing and accumulating an iterable:

* function **accumulate**: take iterable & function, return iterator of accumulated values
* function **foldL0**: fold iterable left with a function
  * raises `StopIteration` exception if iterable is empty
* function **foldL1**: fold iterable left with a function and initial value
* function **mbFoldL**: fold iterable left with an optional initial value
  * wraps result in a `MB` monad
* function **scfoldL**: fold iterable left with premature start and stop conditions
  * wraps result in an `XOR[acc: L, error: str]` monad
* function **scfoldR**: fold iterable right with premature start and stop conditions
  * wraps result in an `XOR[acc: R, error: str]` monad

"""
from __future__ import annotations
from collections.abc import Callable, Iterator, Iterable, Reversible
from enum import auto, Enum
from typing import cast, Final, Never
from circular_array.ca import ca
from .err_handling import MB
from .singletons import NoValue, Sentinel

__all__ = [ 'FM', 'concat', 'merge', 'exhaust',
            'drop', 'dropWhile', 'take', 'takeWhile',
            'accumulate', 'foldL0', 'foldL1',
            'mbFoldL', 'scFoldL', 'scFoldR' ]

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

def dropWhile[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
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

def take[D](iterable: Iterable[D], n: int, /) -> Iterator[D]:
    """Take up to `n` values from `iterable`."""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
            yield value
        except StopIteration:
            break

def takeWhile[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
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

def accumulate[D,L](iterable: Iterable[D],
                    f: Callable[[L, D], L],
                    initial: L|NoValue=NoValue(), /) -> Iterator[L]:
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
    * never returns if `iterable` generates an infinite iterator

    """
    it = iter(iterable)
    try:
        acc = next(it)
    except StopIteration:
        msg = "Attemped to feft fold an empty iterable."
        raise StopIteration(msg)
    for v in it:
        acc = f(acc, v)
    return acc

def foldL1[D, L](iterable: Iterable[D],
                 f: Callable[[L, D], L],
                 initial: L, /) -> L:
    """Folds an iterable left with optional initial value.

    * traditional FP type order given for function `f`
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
    * if iterable empty and no `initial` value given, return empty `MB()`
    * never returns if `iterable` generates an infinite iterator

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
        acc = f(acc, v)
    return MB(acc)

def scFoldL[D,L,S](
        iterable: Iterable[D],
        f: Callable[[L, D], L],
        initial: L|NoValue=NoValue(), /,
        istate_find_start_of_fold: S|Sentinel=Sentinel('fp_iter_scFold'),
        istate_start_of_folding: S|Sentinel=Sentinel('fp_iter_scFold'),
        start_folding: Callable[[D, S], MB[S]]=lambda d, s: MB(),
        stop_folding: Callable[[D, S], MB[S]]=lambda d, s: MB(s),
        include_start_of_fold: bool=True,
        include_end_of_fold: bool=True,
        push_end_back_on_iter: bool=False
    ) -> tuple[MB[L], Iterable[D]]:
    """Short circuit version of a left fold. Useful for infinite or
    non-reversible iterables.

    * Behavior for default arguments will
      * left fold finite iterable
      * start folding immediately
      * continue folding until end (of a possibly infinite iterable)
    * Callable `start_folding` delays starting a left fold
    * Callable `stop_folding` is to prematurely stop the folding left
    * Returns a tuple containing
      * an XOR of either the folded value or error string
      * an iterator values beyond the fold

    """
    it = iter(iterable)
    acc: L

    if initial is not NoValue():
        init = cast(L, initial)
    else:
        try:
            init = cast(L, next(it))
        except StopIteration:
            it = concat((d,), it)
            return MB(), it

    stateMB = cast(MB[S], MB(istate_find_start_of_fold))
    for d in it:
        if (stateMB := startfold(d, stateMB.get())):
            continue
        else:
            if include_start_of_fold:
                it = concat((d,), it)
            break

    stateMB = cast(MB[S], MB(istate_start_of_folding))
    acc = cast(L, df)  # in this case L = D

    for d in it:
        try:
            if (stateMB := stopfold(d, stateMB.get())):
                acc = f(acc, d)
            else:
                if include_stop:
                    acc = f(acc, d)
                else:
                    it = concat((d,), it)
                break
        except Exception:
            return MB(), it

    return MB(acc), it

def scFoldR[D,R,S](iterable: Iterable[D],
        iterable: Iterable[D],
        f: Callable[[D, R], R],
        initial: R|NoValue=NoValue(), /,
        istate_find_start_of_fold: S|Sentinel=Sentinel('fp_iter_scFold'),
        istate_start_of_folding: S|Sentinel=Sentinel('fp_iter_scFold'),
        start_folding: Callable[[D, S], MB[S]]=lambda d, s: MB(),
        stop_folding: Callable[[D, S], MB[S]]=lambda d, s: MB(s),
        include_start_of_fold: bool=True,
        include_end_of_fold: bool=True,
        push_start_back_on_iter: bool=False
    ) -> tuple[MB[R], Iterable[D]]:
    """Short circuit version of a right fold. Useful for infinite or
    non-reversible iterables.

    * Behavior for default arguments will
      * right fold finite iterable
      * start folding at end (of a possibly infinite iterable)
      * continue folding right until beginning
    * Callable `start_folding` prematurely starts a right fold
    * Callable `stop_folding` is to prematurely stop folding right
    * Returns a tuple containing
      * an XOR of either the folded value or error string
      * an iterator values beyond the fold

    """
    it = iter(iterable)
    acc: R

    stateMB = cast(MB[S], MB(istate_find_start_of_fold))
    ds: list[D] = []
    for d in it:
        if (stateMB := startfold(d, stateMB.get())):
            ds.append(d)
        else:
            if include_start:
                ds.append(d)
            else:
                it = concat((d,), it)
            break

    if initial is NoValue():
        if len(ds) == 0:
            return MB(), it
        else:
            acc = cast(R, ds.pop())  # in this case R = D
    else:
        acc = cast(R, initial)

    stateMB = cast(MB[S], MB(istate_foldR))
    while ds:
        if (stateMB := stopfold(d, stateMB.get())):
            acc = f(ds.pop(), acc)
        else:
            if include_stop:
                acc = f(d, acc)
            break

    return MB(acc), it

