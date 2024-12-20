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

from typing import cast, Never
from grscheller.fp.function import swap
from grscheller.fp.iterables import scFoldL, scFoldR
from grscheller.fp.err_handling import MB

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

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert scFoldL(data1, add)[0] == MB(5050)
        assert scFoldR(data1, add)[0] == MB(5050)
        assert scFoldL(data1, add, 10)[0] == MB(5060)
        assert scFoldR(data1, add, 10)[0] == MB(5060)

        assert scFoldL(data2, add)[0] == MB(5049)
        assert scFoldR(data2, add)[0] == MB(5049)
        assert scFoldL(data2, add, 10)[0] == MB(5059)
        assert scFoldR(data2, add, 10)[0] == MB(5059)

        assert scFoldL(data3, add)[0] == MB()
        assert scFoldR(data3, add)[0] == MB()
        assert scFoldL(data3, add, 10)[0] == MB(10)
        assert scFoldR(data3, add, 10)[0] == MB(10)

        assert scFoldL(data4, add)[0] == MB(42)
        assert scFoldR(data4, add)[0] == MB(42)
        assert scFoldL(data4, add, 10)[0] == MB(52)
        assert scFoldR(data4, add, 10)[0] == MB(52)

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int|None] = []
        stuff4: tuple[int|None] = 42,
        stuff5: list[int] = []
        stuff6: tuple[int] = 42,

        assert scFoldL(stuff1, add)[0] == MB(15)
        assert scFoldL(stuff1, add, 10)[0] == MB(25)
        assert scFoldR(stuff1, add)[0] == MB(15)
        assert scFoldR(stuff1, add, 10)[0] == MB(25)
        assert scFoldL(stuff2, add)[0] == MB(14)
        assert scFoldR(stuff2, add)[0] == MB(14)
        assert scFoldL(stuff3, none_add)[0] == MB()
        assert scFoldR(stuff3, none_add)[0].get(None) is None
        assert scFoldL(stuff4, none_add)[0].get(-2) == 42
        assert scFoldR(stuff4, none_add)[0].get(-2) == 42
        assert scFoldL(stuff5, add)[0].get(-2) == -2
        assert scFoldR(stuff5, add)[0].get(-2) == -2
        assert scFoldL(stuff5, add)[0] == MB()
        assert scFoldR(stuff5, add)[0] == MB()
        assert scFoldL(stuff6, add)[0] == MB(42)
        assert scFoldR(stuff6, add)[0] == MB(42)

        assert scFoldL(stuff1, funcL)[0] == MB(-156)
        assert scFoldR(stuff1, funcR)[0] == MB(0)
        assert scFoldL(stuff2, funcL)[0] == MB(84)
        assert scFoldR(stuff2, funcR)[0] == MB(39)
        assert scFoldL(stuff5, funcL)[0] == MB()
        assert scFoldR(stuff5, funcR)[0] == MB()
        assert scFoldL(stuff6, funcL)[0] == MB(42)
        assert scFoldR(stuff6, funcR)[0] == MB(42)

    def test_scfolds(self) -> None:
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

        assert scFoldL(data1, add_or_bail,
                       stopfold=lambda d,s: MB() if d is None else MB(s))[0] == MB(15)
        assert scFoldL(data1, add_or_bail,
                       istate_foldL=0,
                       stopfold=fold_is_lt42_stop_None)[0] == MB()
        assert scFoldL(data2, add,
                       stopfold=fold_is_lt42_stop_NegOne,
                       istate_foldL=0)[0] == MB(15)
        assert scFoldL(data3, add,
                       stopfold=fold_is_lt42,
                       istate_foldL=0)[0] == MB(36)
        assert scFoldL(data4, add,
                       stopfold=fold_is_lt42,
                       istate_foldL=0)[0] == MB(21)
        assert scFoldL(data5, add,
                       stopfold=fold_is_lt42,
                       istate_foldL=0)[0] == MB()
        assert scFoldL(data6, add,
                       stopfold=fold_is_lt42,
                       istate_foldL=0)[0] == MB(10)
        assert scFoldL(data7, add,
                       stopfold=fold_is_lt42,
                       istate_foldL=0)[0] == MB(35)
        assert scFoldL(data1, add_or_bail, 10,
                       stopfold=fold_is_lt42_stop_None,
                       istate_foldL=10)[0] == MB()
        assert scFoldL(data1, add_or_bail, 10,
                       stopfold=fold_is_lt42_stop_None,
                       istate_foldL=10)[0] == MB(25)
        assert scFoldL(data2, add, 10,
                       stopfold=fold_is_lt42_stop_NegOne,
                       istate_foldL=10)[0] == MB(25)
        assert scFoldL(data2, add, 10,
                       stopfold=fold_is_lt42_stop_NegOne,
                       include_stop=True,
                       istate_foldL=10)[0] == MB(24)
        assert scFoldL(data3, add, 10,
                       stopfold=fold_is_lt42,
                       istate_foldL=10)[0] == MB(38)
        assert scFoldL(data4, add, 20,
                       stopfold=fold_is_lt42,
                       istate_foldL=20)[0] == MB(41)
        assert scFoldL(data5, add, 10,
                       stopfold=fold_is_lt42,
                       istate_foldL=10)[0] == MB(10)
        assert scFoldL(data6, add, 10,
                       stopfold=fold_is_lt42,
                       istate_foldL=10)[0] == MB(20)
        assert scFoldL(data7, add, 10,
                       stopfold=fold_is_lt42,
                       istate_foldL=10)[0] == MB(25)
        assert scFoldR(data1, add_or_bail,
                       startfold=fold_is_lt42_stop_None,
                       include_stop=False,
                       istate_foldR=0)[0] == MB(15)
        assert scFoldR(data2, add,
                       startfold=fold_is_lt42_stop_NegOne,
                       include_stop=False,
                       istate_foldR=0)[0] == MB(15)
        assert scFoldR(data3, add,
                       startfold=fold_is_lt42,
                       istate_foldR=0,
                       include_stop=False)[0] == MB(36)
        assert scFoldR(data4, add,
                       startfold=fold_is_lt42,
                       istate_foldR=0)[0] == MB(21)
        assert scFoldR(data5, add,
                       startfold=fold_is_lt42,
                       istate_foldR=0)[0] == MB()
        assert scFoldR(data6, add,
                       startfold=fold_is_lt42,
                       istate_foldR=0)[0] == MB(10)
        assert scFoldR(data7, add,
                       startfold=fold_is_lt42,
                       istate_foldR=0)[0] == MB(35)
        assert scFoldR(data1, add_or_bail, 10,
                       startfold=fold_is_lt42_stop_None,
                       istate_foldR=10)[0] == MB(25)
        assert scFoldR(data2, add, 10,
                       startfold=fold_is_lt42_stop_NegOne,
                       istate_foldR=10)[0] == MB(25)
        assert scFoldR(data3, add, 10,
                       startfold=fold_is_lt42,
                       istate_foldR=10)[0] == MB(38)
        assert scFoldR(data4, add, 20,
                       startfold=fold_is_lt42,
                       istate_foldR=20)[0] == MB(41)
        assert scFoldR(data5, add, 10,
                       startfold=fold_is_lt42,
                       istate_foldR=10)[0] == MB(10)
        assert scFoldR(data6, add, 10,
                       startfold=fold_is_lt42,
                       istate_foldR=10)[0] == MB(20)
        assert scFoldR(data7, add, 10,
                       startfold=fold_is_lt42,
                       istate_foldR=10)[0] == MB(25)
