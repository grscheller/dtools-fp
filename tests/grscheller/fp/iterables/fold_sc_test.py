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

from typing import Optional, cast, Never
from grscheller.fp.iterables import foldLsc, foldRsc
from grscheller.fp.nada import Nada, nada
from grscheller.fp.woException import MB

class Test_fp_no_sc_folds:
    def test_fold(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii+jj

        def none_add(ii: int|None, jj: int|None) -> int|None:
            if ii is None:
                ii = 0
            if jj is None:
                jj = 0
            return ii+jj

        def nada_add(ii: int|Nada, jj: int|Nada) -> int|Nada:
            if ii is nada:
                i = 0
            else:
                i = cast(int, ii)
            if jj is nada:
                j = 0
            else:
                j = cast(int, jj)
            return i+j

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert foldLsc(data1, add) == MB(5050)
        assert foldRsc(data1, add) == MB(5050)
        assert foldLsc(data1, add, 10) == MB(5060)
        assert foldRsc(data1, add, 10) == MB(5060)

        assert foldLsc(data2, add) == MB(5049)
        assert foldRsc(data2, add) == MB(5049)
        assert foldLsc(data2, add, 10) == MB(5059)
        assert foldRsc(data2, add, 10) == MB(5059)

        assert foldLsc(data3, add) == MB()
        assert foldRsc(data3, add) == MB()
        assert foldLsc(data3, add, 10) == MB(10)
        assert foldRsc(data3, add, 10) == MB(10)

        assert foldLsc(data4, add) == MB(42)
        assert foldRsc(data4, add) == MB(42)
        assert foldLsc(data4, add, 10) == MB(52)
        assert foldRsc(data4, add, 10) == MB(52)

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int|None] = []
        stuff4: tuple[int|Nada] = 42,
        stuff5: list[int] = []
        stuff6: tuple[int] = 42,

        assert foldLsc(stuff1, add) == MB(15)
        assert foldLsc(stuff1, add, 10) == MB(25)
        assert foldRsc(stuff1, add) == MB(15)
        assert foldRsc(stuff1, add, 10) == MB(25)
        assert foldLsc(stuff2, add) == MB(14)
        assert foldRsc(stuff2, add) == MB(14)
        assert foldLsc(stuff3, none_add) == MB()
        assert foldRsc(stuff3, none_add).get(None) is None
        assert foldLsc(stuff4, nada_add).get(-2) == 42
        assert foldRsc(stuff4, nada_add).get(-2) == 42
        assert foldLsc(stuff5, add).get(-2) == -2
        assert foldRsc(stuff5, add).get(-2) == -2
        assert foldLsc(stuff5, add) == MB()
        assert foldRsc(stuff5, add) == MB()
        assert foldLsc(stuff6, add) == MB(42)
        assert foldRsc(stuff6, add) == MB(42)

        assert foldLsc(stuff1, funcL) == MB(-156)
        assert foldRsc(stuff1, funcR) == MB(0)
        assert foldLsc(stuff2, funcL) == MB(84)
        assert foldRsc(stuff2, funcR) == MB(39)
        assert foldLsc(stuff5, funcL) == MB()
        assert foldRsc(stuff5, funcR) == MB()
        assert foldLsc(stuff6, funcL) == MB(42)
        assert foldRsc(stuff6, funcR) == MB(42)

    def test_fold_sc(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii + jj

        def add_or_bail(ii: int|None, jj: int|None) -> int|Never:
            if ii is None or jj is None:
                raise Exception
            return ii + jj

        def fold_is_lt42(d: int, fold_total: int) -> MB[int]:
            fold_total += d
            if fold_total < 42:
                return MB(fold_total)
            else:
                return MB()

        def fold_is_lt42_stop_None(d: int|None, fold_total: int) -> MB[int]:
            if d is None:
                return MB()
            else:
                fold_total += d
                if fold_total < 42:
                    return MB(fold_total)
                else:
                    return MB()

        def fold_is_lt42_stop_NegOne(d: int, fold_total: int) -> MB[int]:
            if d == -1:
                return MB()
            else:
                fold_total += d
                if fold_total < 42:
                    return MB(fold_total)
                else:
                    return MB()

        data1 = (1, 2, 3, 4, 5, None, 6, 7, 8, 9, 10)
        data2 = (1, 2, 3, 4, 5, -1, 6, 7, 8, 9, 10)
        data3 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data4 = [1, 2, 3, 4, 5, 6]
        data5: tuple[int, ...] = ()
        data6 = 10,
        data7 = 15, 20, 25, 30

        assert foldLsc(data1, add_or_bail, stopfold=fold_is_lt42_stop_None, istate=0) == MB(15)
        assert foldLsc(data2, add, stopfold=fold_is_lt42_stop_NegOne, istate=0) == MB(15)
        assert foldLsc(data3, add, stopfold=fold_is_lt42, istate=0) == MB(36)
        assert foldLsc(data4, add, stopfold=fold_is_lt42, istate=0) == MB(21)
        assert foldLsc(data5, add, stopfold=fold_is_lt42, istate=0) == MB()
        assert foldLsc(data6, add, stopfold=fold_is_lt42, istate=0) == MB(10)
        assert foldLsc(data7, add, stopfold=fold_is_lt42, istate=0) == MB(35)
        assert foldLsc(data1, add_or_bail, 10, stopfold=fold_is_lt42_stop_None, istate=10) == MB(25)
        assert foldLsc(data2, add, 10, stopfold=fold_is_lt42_stop_NegOne, istate=10) == MB(25)
        assert foldLsc(data3, add, 10, stopfold=fold_is_lt42, istate=10) == MB(38)
        assert foldLsc(data4, add, 20, stopfold=fold_is_lt42, istate=20) == MB(41)
        assert foldLsc(data5, add, 10, stopfold=fold_is_lt42, istate=10) == MB(10)
        assert foldLsc(data6, add, 10, stopfold=fold_is_lt42, istate=10) == MB(20)
        assert foldLsc(data7, add, 10, stopfold=fold_is_lt42, istate=10) == MB(25)

        assert foldRsc(data1, add_or_bail, stopfold=fold_is_lt42_stop_None, istate=0) == MB(15)
        assert foldRsc(data2, add, stopfold=fold_is_lt42_stop_NegOne, istate=0) == MB(15)
        assert foldRsc(data3, add, stopfold=fold_is_lt42, istate=0) == MB(36)
        assert foldRsc(data4, add, stopfold=fold_is_lt42, istate=0) == MB(21)
        assert foldRsc(data5, add, stopfold=fold_is_lt42, istate=0) == MB()
        assert foldRsc(data6, add, stopfold=fold_is_lt42, istate=0) == MB(10)
        assert foldRsc(data7, add, stopfold=fold_is_lt42, istate=0) == MB(35)
        assert foldRsc(data1, add_or_bail, 10, stopfold=fold_is_lt42_stop_None, istate=10) == MB(25)
        assert foldRsc(data2, add, 10, stopfold=fold_is_lt42_stop_NegOne, istate=10) == MB(25)
        assert foldRsc(data3, add, 10, stopfold=fold_is_lt42, istate=10) == MB(38)
        assert foldRsc(data4, add, 20, stopfold=fold_is_lt42, istate=20) == MB(41)
        assert foldRsc(data5, add, 10, stopfold=fold_is_lt42, istate=10) == MB(10)
        assert foldRsc(data6, add, 10, stopfold=fold_is_lt42, istate=10) == MB(20)
        assert foldRsc(data7, add, 10, stopfold=fold_is_lt42, istate=10) == MB(25)
