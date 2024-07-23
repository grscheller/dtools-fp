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
from grscheller.fp.nothing import Nothing, nothing

def add2(x: int) -> int:
    return x + 2

def gt42(x: int) -> bool|Nothing:
    if x > 42:
        return True
    if x >= 0:
        return False
    return Nothing()

class Test_Nothing:
    def test_identity(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        no3 = nothing
        assert no1 is no1
        assert no1 is no2
        assert no3 is no1
        assert no2 is nothing
        if no1 is not no2:
            assert False
        else:
            assert True

    def test_equality(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        no3 = nothing
        assert no1 == no1
        assert no2 == no2
        assert no3 == no2
        assert no1 == no2
        assert no2 == no1
        assert no1 == nothing
        if no1 != no2:
            assert False
        else:
            assert True

    def test_iterate(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        no3 = nothing
        l1 = [42]
        v: int
        for v in no1:
            l1.append(v)
        for v in no2:
            assert False
        assert len(l1) == 1

    def test_len(self) -> None:
        no1 = Nothing()
        assert len(no1) == 0

    def test_get(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        assert no1.get(42) == 42
        assert no2.get(21) == 21
        got1 = no1.get()
        got2 = no1.get('forty-two')
        assert got1 is Nothing()
        assert got2 is 'forty-two'
        assert got2 == 'forty-two'
        assert no2.get(13) == (10 + 3)
        assert no2.get(10//7) == 10//7

    def test_equal_self(self) -> None:
        no1 = Nothing()
        no1 == no1
        no1.get(42) == no1.get(42)
        no1.get(42) != no1.get(21)

    def test_map(self) -> None:
        no1 = Nothing()
        no2 = no1.map(add2)
        assert no1 == no2 == Nothing()
        assert no1 is no2 is Nothing()

    def test_call(self) -> None:
        no1 = Nothing()
        assert no1() is Nothing()
        assert no1() is nothing
        assert nothing() is nothing
        assert no1(42) is Nothing()
        assert no1(a=1, b=2) is Nothing()

    def test_get_set(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        got = no1[42]
        no2[5] = 101
        assert no1 == no2 == nothing
        assert got == nothing
        assert no1[2:7:1] == nothing
        no2[1:4] == 1,2,3,4,5,6,7
        assert no2 is nothing

    def test_arbitrary_methods(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        assert no1.foo(23, 12, bar='five') is nothing

    def test_add_mul(self) -> None:
        no1 = Nothing()
        no2 = Nothing()
        assert 2 + 3 == 5
        assert no2 + 99 == no1
        assert 86 + no1 == no2
        assert no2 * 99 == no1
        assert 86 * no1 == no2
