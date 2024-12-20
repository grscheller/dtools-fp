# Copyright 2024 Geoffrey R. Scheller
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

"""### Module fp.state - state monad

Implementing a

#### Pure FP State handling type:


"""
from __future__ import annotations

__all__ = [ 'State' ]

from collections.abc import Callable, Sequence
from typing import Final
from fp.singletons import NoValue

class State[S, A]():
    """State Monad - data structure to generate values while propagating changes
    of state.

    * class **State**: A pure FP immutable implementation of the State Monad
      * translated to Python from the book "Functional Programming in Scala"
        * authors Chiusana & Bjarnason
      * the `run` method ...
      * very multi-thread safe assuming contained state is not shared

    """
    __slots__ = '_run'
    __match_args__ = '_run'

    @staticmethod
    def unit[S1, B](b: B) -> State[S1, B]:
        """Creat a State action from a value."""
        return State(lambda s: (b, s))
 
    @staticmethod
    def get[S1]() -> State[S1, S1]:
        """Set run action to return the current state

        * the run action will yield the current state
        * the current state is propagated unchanged

        """
        return State[S1, S1](lambda s: (s, s))

    @staticmethod
    def set[S1](s: S1) -> State[S1, tuple[()]]:
        """Manually set a state.

        * the run action ignores previous state
        * the run action returns a canonically meaningless value

        """
        return State(lambda _: ((), s))

    def __init__(self, run: Callable[[S], tuple[A, S]]) -> None:
        self._run = run

    def flatmap[B](self, g: Callable[[A], State[S, B]]) -> State[S, B]:
        def foo(s: S) -> tuple[B, S]:
            a, s1 = self._run(s)
            return g(a)._run(s1) 
        return State(lambda s: foo(s))

    def map[B](self, f: Callable[[A], B]) -> State[S, B]:
        return self.flatmap(lambda a: State.unit(f(a)))

    def map2[B, C](self, sb: State[S, B], f: Callable[[A, B], C]) -> State[S, C]:
        return self.flatmap(lambda a: sb.map(lambda b: f(a, b)))

    def both[B](self, rb: State[S, B]) -> State[S, tuple[A, B]]:
        return self.map2(rb, lambda u, v: (u, v))
