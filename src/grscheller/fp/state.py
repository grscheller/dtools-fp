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

* in a pure functional language you don't extract the value from a monad
  * it would be unPythonic to force FP on the user of this package
    * pushing an imperative algorithms to an intermost scope would be a use case
    * not sure if I will ever get to "monad transformers" with this project
    * therefore an "escape hatch" is needed at the end of a flatmap chain

"""
from __future__ import annotations

__all__ = [ 'State' ]

from collections.abc import Callable

class State[S, A]():
    """State Monad - data structure to generate values while propagating changes
    of state.

    * class **State**: A pure FP immutable implementation of the State Monad
      * translated to Python from the book "Functional Programming in Scala"
        * authors Chiusana & Bjarnason
      * class `State` represents neither a state nor (value, state) pair
        * it wraps a transformation old_state -> (value, new_state)
        * the "private" `_run` method is this wrapped transformation

    """
    __slots__ = 'run'

    @staticmethod
    def unit[S1, B](b: B) -> State[S1, B]:
        """Create a State action from a value."""
        return State(lambda s: (b, s))
 
    # FP programming interface

    @staticmethod
    def set[S1](s: S1) -> State[S1, tuple[()]]:
        """Manually set a state.

        * the run action
          * ignores previous state
          * generates a canonically meaningless value and given state `s: S1`

        """
        return State(lambda _: ((), s))

    @staticmethod
    def get[S1]() -> State[S1, S1]:
        """Set run action to return the current state

        * the run action yields the current state
        * the current state is propagated unchanged

        """
        return State[S1, S1](lambda s: (s, s))

    # OOP programming interface

    def __init__(self, run: Callable[[S], tuple[A, S]]) -> None:
        self.run = run

    def flatmap[B](self, g: Callable[[A], State[S, B]]) -> State[S, B]:
        def compose(s: S) -> tuple[B, S]:
            a, s1 = self.run(s)
            return g(a).run(s1) 
        return State(lambda s: compose(s))

    def map[B](self, f: Callable[[A], B]) -> State[S, B]:
        return self.flatmap(lambda a: State.unit(f(a)))

    def map2[B, C](self, sb: State[S, B], f: Callable[[A, B], C]) -> State[S, C]:
        return self.flatmap(lambda a: sb.map(lambda b: f(a, b)))

    def both[B](self, rb: State[S, B]) -> State[S, tuple[A, B]]:
        return self.map2(rb, lambda a, b: (a, b))

