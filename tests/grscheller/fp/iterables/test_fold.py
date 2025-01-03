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

from grscheller.fp.iterables import foldL0, foldL1, mbFoldL
from grscheller.fp.err_handling import MB

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

        assert foldL0(data1, add2) == 5050
        assert foldL1(data1, add2, 10) == 5060

        assert foldL0(data2, add2) == 5049
        assert foldL1(data2, add2, 10) == 5059

        assert foldL1(data3, add2, 0) == 0
        assert foldL1(data3, add2, 10) == 10

        assert foldL0(data4, add2) == 42
        assert foldL1(data4, add2, 10) == 52

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert foldL0(stuff1, add2) == 15
        assert foldL1(stuff1, add2, 10) == 25
        assert foldL0(stuff2, add2) == 14
        assert foldL1(stuff3, add2, 0) == 0
        assert foldL1(stuff3, add2, -42) == -42
        assert foldL0(stuff4, add2) == 42
        assert foldL0(stuff4, add2) == 42

        assert foldL0(stuff1, funcL) == -156
        assert foldL0(stuff2, funcL) == 84
        assert foldL1(stuff3, funcL, 0) == 0
        assert foldL1(stuff3, funcL, -1) == -1
        assert foldL0(stuff4, funcL) == 42
        assert foldL0(stuff1, funcL) == -156
        assert foldL0(stuff2, funcL) == 84
        assert foldL0(stuff2, funcL) == 84

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

