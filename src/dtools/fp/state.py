# Copyright 2024-2025 Geoffrey R. Scheller
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

Handling state functionally.

#### Pure FP State handling type:

* class **State**: A pure FP immutable implementation for the State Monad
  * translated to Python from the book "Functional Programming in Scala"
    * authors Chiusana & Bjarnason
  * using `bind` instead of `flatmap`
    * I feel `flatmap` is misleading for non-container-like monads
    * flatmap name too long
      * without do-notation code tends to march to the right
      * `bind` for state monad is part of the user API
        * shorter to type
        * less of just an implementation detail

"""
from __future__ import annotations

__all__ = [ 'State' ]

from collections.abc import Callable
from typing import Any, Never
from dtools.circular_array.ca import ca

class State[S, A]():
    """Data structure generating values while propagating changes of state.

    * class `State` represents neither a state nor (value, state) pair
      * it wraps a transformation old_state -> (value, new_state)
      * the `run` method is this wrapped transformation
    * `bind` is just state propagating function composition
      * `bind` is sometimes called "flatmap"

    """
    __slots__ = 'run'

    def __init__(self, run: Callable[[S], tuple[A, S]]) -> None:
        self.run = run

    def bind[B](self, g: Callable[[A], State[S, B]]) -> State[S, B]:
        def compose(s: S) -> tuple[B, S]:
            a, s1 = self.run(s)
            return g(a).run(s1)
        return State(compose)

    def map[B](self, f: Callable[[A], B]) -> State[S, B]:
        return self.bind(lambda a: State.unit(f(a)))

    def map2[B, C](self, sb: State[S, B], f: Callable[[A, B], C]) -> State[S, C]:
        return self.bind(lambda a: sb.map(lambda b: f(a, b)))

    def both[B](self, rb: State[S, B]) -> State[S, tuple[A, B]]:
        return self.map2(rb, lambda a, b: (a, b))

    @staticmethod
    def unit[S1, B](b: B) -> State[S1, B]:
        """Create a State action from a value."""
        return State(lambda s: (b, s))

    @staticmethod
    def get[S1]() -> State[S1, S1]:
        """Set run action to return the current state

        * the current state is propagated unchanged
        * current value now set to current state

        """
        return State[S1, S1](lambda s: (s, s))

    @staticmethod
    def set[S1](s: S1) -> State[S1, tuple[()]]:
        """Manually set a state.

        * the run action
          * ignores previous state and swaps in a new state
          * assigns a canonically meaningless value to current value

        """
        return State(lambda _: ((), s))

    @staticmethod
    def modify[S1](f: Callable[[S1], S1]) -> State[S1, tuple[()]]:
        return State.get().bind(lambda a: State.set(f(a)))

    @staticmethod
    def sequence[S1, A1](sas: list[State[S1, A1]]) -> State[S1, list[A1]]:
        """Combine a list of state actions into a state action of a list.

        * all state actions must be of the same type
        * run method evaluates list front to back

        """
        def append_ret(a: A1, l: list[A1]) -> list[A1]:
            l.append(a)
            return l

        return ca(sas).foldL(lambda sa, s1: s1.map2(sa, append_ret), State.unit(list[A1]([])))

