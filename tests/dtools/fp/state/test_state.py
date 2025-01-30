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

from typing import Final, Never
from dtools.fp.state import State

class Test_simple:
    def test_simple_counter(self) -> None:
        sc = State(lambda s: (s+1, s+1))

        aa, ss = sc.run(0)
        assert (aa, ss) == (1, 1)

        aa, ss = sc.run(42)
        assert (aa, ss) == (43, 43)

        sc1 = sc.bind(lambda a: sc)
        aa, ss = sc1.run(0)
        assert (aa, ss) == (2, 2)

        sc2 = sc.bind(lambda a: sc)
        aa, ss = sc2.run(40)
        assert (aa, ss) == (42, 42)

        start = State.set(0)
        sc3 = start.bind(lambda a: sc)
        aa, ss = sc3.run(40)
        assert (aa, ss) == (1, 1)

        sc4 = sc.bind(lambda a: sc).bind(lambda a: sc)
        aa, ss = sc4.run(0)
        assert (aa, ss) == (3, 3)
        aa, ss = sc4.run(0)
        assert (aa, ss) == (3, 3)

        sc4 = sc4.bind(lambda a: sc1)
        aa, ss = sc4.run(5)
        assert aa == 10
        assert ss == 10

        a1, s1 = sc.run(5)
        a2, s2 = sc.run(s1)
        assert (a1, s1) == (6, 6)
        assert (a2, s2) == (7, 7)

    def test_mod3_count(self) -> None:
        m3 = State(lambda s: (s, (s+1)%3))

        a, s = m3.run(1)
        assert a == 1
        a, s = m3.run(s)
        assert a == 2
        a, s = m3.run(s)
        assert a == 0
        a, s = m3.run(s)
        assert a == 1
        a, s = m3.run(s)
        assert a == 2

    def test_blast_off(self) -> None:
        countdown = State(lambda s: (s, s-1))
        blastoff = countdown.bind(
            lambda a: State(lambda a: ('Blastoff!', 5) if a == -1 else (a+1, a))
        )

        a, s = blastoff.run(11)
        assert (a, s) == (11, 10)

        for cnt in range(10, 0, -1):
            a, s = blastoff.run(s)
            assert cnt == a

        a, s = blastoff.run(s)
        assert (a, s) == ('Blastoff!', 5)

        for cnt in range(5, 0, -1):
            a, s = blastoff.run(s)
            assert cnt == a

        a, s = blastoff.run(s)
        assert (a, s) == ('Blastoff!', 5)

    def test_modify(self) -> None:
        count: Final[State[int, int]] = State(lambda s: (s, s+1))
        square_state = State.modify(lambda n: n*n)

        def cnt(a: int) -> State[int, int]:
            return count

        def sqr_st(a: int) -> State[int, tuple[()]]:
            return square_state

        do_it = count.bind(cnt).bind(cnt).bind(sqr_st).bind(cnt).bind(sqr_st).bind(cnt)
        a, s = do_it.run(0)
        assert (a, s) == (100, 101)
