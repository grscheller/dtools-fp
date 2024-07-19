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

from __future__ import annotations

from typing import Optional
from grscheller.fp.bottom import Opt

def add2(x: int) -> int:
    return x + 2

def gt42(x: int) -> Optional[bool]:
    if x > 42:
        return True
    if x == 42:
        return False
    return None

class TestOpt:
    def test_identity(self) -> None:
        n1: Opt[int] = Opt()
        n2: Opt[int] = Opt()
        o1 = Opt(42)
        o2 = Opt(40)
        assert o1 is o1
        assert o1 is not o2
        o3 = o2.map_(add2)
        assert o3 is not o2
        assert o1 is not o3
        assert n1 is n1
        assert n1 is not n2
        assert o1 is not n1
        assert n2 is not o2

    def test_equality(self) -> None:
        n1: Opt[int] = Opt()
        n2: Opt[int] = Opt()
        o1 = Opt(42)
        o2 = Opt(40)
        assert o1 == o1
        assert o1 != o2
        o3 = o2.map_(add2)
        assert o3 != o2
        assert o1 == o3
        assert n1 == n1
        assert n1 == n2
        assert o1 != n1
        assert n2 != o2

    def test_iterate(self) -> None:
        o1 = Opt(38)
        o2 = o1.map_(add2).map_(add2)
        n1: Opt[int] = Opt()
        l1 = []
        l2 = []
        for v in n1:
            l1.append(v)
        for v in o2:
            l2.append(v)
        assert len(l1) == 0
        assert len(l2) == 1
        assert l2[0] == 42

    def test_get_(self) -> None:
        o1 = Opt(1)
        n1: Opt[int] = Opt()
        assert o1.get_(42) == 1
        assert n1.get_(21) == 21
        assert o1.get_() == 1
        try:
            foo: Optional[int] = 42
            foo = n1.get_()
        except ValueError:
            assert True
        else:
            assert False
        finally:
            assert foo == 42
        assert n1.get_(13) == (10 + 3)
        assert n1.get_(10//7) == 10//7

    def test_equal_self(self) -> None:
        opt42 = Opt(40+2)
        optno: Opt[int] = Opt()
        opt42 != optno
        opt42 == opt42
        optno == optno

    def test_map_(self) -> None:
        l1 = [1, 2, 3]
        l2 = [5, 3]
        optl1 = Opt(l1)
        optl2 = Opt(l2)
        opt1 = optl1.map_(lambda l: sum(l))
        opt2 = optl2.map_(lambda l: l + [42])
        opt3 = optl2.map_(lambda l: l.append(42))
        assert opt1 == Opt(6)
        assert l2 == [5, 3, 42]
        assert opt2 == Opt([5, 3, 42])
        assert opt3 == Opt()

    def test_map(self) -> None:
        l1 = [1, 2, 3]
        l2 = [5, 3]
        l0: list[int] = []
        optl1 = Opt(l1)
        optl2 = Opt(l2)
        optl0 = Opt(l0)
        optlNo: Opt[list[int]] = Opt()
        opt1 = optl1.map(lambda x: x + 2)
        opt2 = optl2.map(lambda x: [x]*x)
        opt0 = optl0.map(lambda x: [x]*x)
        optNo = optlNo.map(lambda x: [x]*x)
        assert opt1 == Opt([3, 4, 5])
        assert opt2 == Opt([[5, 5, 5, 5, 5], [2, 2]])
        assert opt0 == Opt([])
        assert optNo == Opt()
