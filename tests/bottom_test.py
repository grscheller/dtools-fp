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
from grscheller.fp.bottom import Bottom

def add2(x: int) -> int:
    return x + 2

def gt42(x: int) -> bool|Bottom:
    if x > 42:
        return True
    if x >= 0:
        return False
    return Bottom()

class Test_Bottom:
    def test_identity(self) -> None:
        bot1 = Bottom()
        bot2 = Bottom()
        assert bot1 is bot1
        assert bot1 is bot2

    def test_equality(self) -> None:
        bot1 = Bottom()
        bot2 = Bottom()
        assert bot1 == bot1
        assert bot2 == bot2
        assert bot1 == bot2
        assert bot2 == bot1

    def test_iterate(self) -> None:
        bot1 = Bottom()
        bot2 = Bottom()
        l1 = [42]
        for v in bot1:
            l1.append(v)
        for v in bot2:
            assert False
        assert len(l1) == 1

    def test_get(self) -> None:
        bot1 = Bottom()
        bot2 = Bottom()
        assert bot1.get(42) == 42
        assert bot2.get(21) == 21
        try:
            foo = 42
            foo = bot2.get()
        except ValueError:
            assert True
        else:
            assert False
        finally:
            assert foo == 42
        assert bot2.get(13) == (10 + 3)
        assert bot2.get(10//7) == 10//7

    def test_equal_self(self) -> None:
        bot1 = Bottom()
        bot1 == bot1
        bot1.get(42) == bot1.get(42)
        bot1.get(42) != bot1.get(21)

    def test_map(self) -> None:
        bot1 = Bottom()
        bot2 = bot1.map(add2)
        assert bot1 == bot2 == Bottom()
        assert bot1 is bot2 is Bottom()
