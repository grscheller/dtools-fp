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

from collections.abc import Callable
from dtools.fp.iterables import reduceL, foldL, mbFoldL, scReduceL, scReduceR
from dtools.fp.err_handling import MB

class Test_fp_folds:
    def test_fold(self) -> None:
        def add2(ii: int, jj: int) -> int:
            return ii+jj

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert reduceL(data1, add2) == 5050
        assert foldL(data1, add2, 10) == 5060

        assert reduceL(data2, add2) == 5049
        assert foldL(data2, add2, 10) == 5059

        assert foldL(data3, add2, 0) == 0
        assert foldL(data3, add2, 10) == 10

        assert reduceL(data4, add2) == 42
        assert foldL(data4, add2, 10) == 52

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert reduceL(stuff1, add2) == 15
        assert foldL(stuff1, add2, 10) == 25
        assert reduceL(stuff2, add2) == 14
        assert foldL(stuff3, add2, 0) == 0
        assert foldL(stuff3, add2, -42) == -42
        assert reduceL(stuff4, add2) == 42
        assert reduceL(stuff4, add2) == 42

        assert reduceL(stuff1, funcL) == -156
        assert reduceL(stuff2, funcL) == 84
        assert foldL(stuff3, funcL, 0) == 0
        assert foldL(stuff3, funcL, -1) == -1
        assert reduceL(stuff4, funcL) == 42
        assert reduceL(stuff1, funcL) == -156
        assert reduceL(stuff2, funcL) == 84
        assert reduceL(stuff2, funcL) == 84

class Test_fp_mbFolds:
    def test_mbFold(self) -> None:
        def add2(ii: int, jj: int) -> int:
            return ii+jj

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert mbFoldL(data1, add2) == MB(5050)
        assert mbFoldL(data1, add2, 10) == MB(5060)

        assert mbFoldL(data2, add2) == MB(5049)
        assert mbFoldL(data2, add2, 10) == MB(5059)

        assert mbFoldL(data3, add2) == MB()
        assert mbFoldL(data3, add2, 10) == MB(10)

        assert mbFoldL(data4, add2) == MB(42)
        assert mbFoldL(data4, add2, 10) == MB(52)

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert mbFoldL(stuff1, add2) == MB(15)
        assert mbFoldL(stuff1, add2, 10) == MB(25)
        assert mbFoldL(stuff2, add2) == MB(14)
        assert mbFoldL(stuff3, add2) == MB()
        assert mbFoldL(stuff4, add2) == MB(42)
        assert mbFoldL(stuff4, add2).get(-1) == 42
        assert mbFoldL(stuff3, add2).get(-1) == -1

        assert mbFoldL(stuff1, funcL) == MB(-156)
        assert mbFoldL(stuff2, funcL) == MB(84)
        assert mbFoldL(stuff3, funcL) == MB()
        assert mbFoldL(stuff3, funcL).get(-1) == -1
        assert mbFoldL(stuff4, funcL) == MB(42)
        assert mbFoldL(stuff1, funcL) == MB(-156)
        assert mbFoldL(stuff2, funcL) == MB(84)
        assert mbFoldL(stuff2, funcL).get() == 84

class Test_fp_scReduceL:

    def test_defaults(self) -> None:
        add2: Callable[[int, int], int] = lambda a, b: a+b

        stuff = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        sum55, it = scReduceL(stuff, add2)
        assert sum55 == 55
        try:
            nono = next(it)
        except StopIteration:
            assert True
        else:
            assert False

    def test_start_stop(self) -> None:
        add2: Callable[[int, int], int] = lambda a, b: a+b

        stuff = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        def ge2(a: int) -> bool:
            return a >= 2

        def ge8(a: int) -> bool:
            return a >= 9

        sum35, it = scReduceL(stuff, add2, start=ge2, stop=ge8)
        assert sum35 == 35
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert int9 == 9

class Test_fp_scReduceR:

    def test_defaults(self) -> None:
        add2: Callable[[int, int], int] = lambda a, b: a+b

        stuff = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        sum55, it = scReduceR(stuff, add2)
        assert sum55 == 55
        try:
            nono = next(it)
        except StopIteration:
            assert True
        else:
            assert False

    def test_start_stop(self) -> None:
        add2: Callable[[int, int], int] = lambda a, b: a+b

        stuff = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        def ge2(a: int) -> bool:
            return a >= 2

        def ge8(a: int) -> bool:
            return a >= 9

        sum35, it = scReduceR(stuff, add2, start=ge8, stop=ge2)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert int9 == 9
        assert sum35 == 35

