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

from typing import Optional
from grscheller.fp.iterables import foldL_sc, foldR_sc
from grscheller.fp.nada import Nada, nada
from grscheller.fp.woException import MB

class Test_fp_no_sc_folds:
    def test_fold(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii+jj

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert foldL_sc(data1, add) == 5050
        assert foldR_sc(data1, add) == 5050
        assert foldL_sc(data1, add, 10) == 5060
        assert foldR_sc(data1, add, 10) == 5060

        assert foldL_sc(data2, add) == 5049
        assert foldR_sc(data2, add) == 5049
        assert foldL_sc(data2, add, 10) == 5059
        assert foldR_sc(data2, add, 10) == 5059

        assert foldL_sc(data3, add) is None
        assert foldR_sc(data3, add) is None
        assert foldL_sc(data3, add, 10) == 10
        assert foldR_sc(data3, add, 10) == 10

        assert foldL_sc(data4, add) == 42
        assert foldR_sc(data4, add) == 42
        assert foldL_sc(data4, add, 10) == 52
        assert foldR_sc(data4, add, 10) == 52

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert foldL_sc(stuff1, add, sent=None) == 15
        assert foldL_sc(stuff1, add, None, sent=None) == 15
        assert foldL_sc(stuff1, add, 10, sent=None) == 25
        assert foldR_sc(stuff1, add, sent=None) == 15
        assert foldL_sc(stuff2, add, sent=None) == 14
        assert foldR_sc(stuff2, add, sent=None) == 14
        assert foldL_sc(stuff3, add, sent=None) is None
        assert foldR_sc(stuff3, add, sent=None) is None
        assert foldL_sc(stuff4, add, sent=None) == 42
        assert foldR_sc(stuff4, add, sent=None) == 42
        assert foldL_sc(stuff3, add, sent=nada) is nada
        assert foldL_sc(stuff3, add, sent=nada) != nada
        assert foldL_sc(stuff3, add) is None
        assert foldR_sc(stuff3, add) is None
        assert foldL_sc(stuff4, add) == 42
        assert foldR_sc(stuff4, add) == 42

        assert foldL_sc(stuff1, funcL, sent=nada) == -156
        assert foldR_sc(stuff1, funcR, sent=nada) == 0
        assert foldL_sc(stuff2, funcL, sent=nada) == 84
        assert foldR_sc(stuff2, funcR, sent=nada) == 39
        assert foldL_sc(stuff3, funcL, sent=nada) is nada
        assert foldR_sc(stuff3, funcR, sent=nada) is nada
        assert foldL_sc(stuff4, funcL) == 42
        assert foldR_sc(stuff4, funcR, sent=nada) == 42
        assert foldL_sc(stuff1, funcL) == -156
        assert foldR_sc(stuff1, funcR) == 0
        assert foldL_sc(stuff2, funcL) == 84
        assert foldR_sc(stuff2, funcR) == 39
        assert foldL_sc(stuff3, funcL) is None
        assert foldR_sc(stuff3, funcR) is None
        assert foldL_sc(stuff4, funcL) == 42
        assert foldR_sc(stuff4, funcR) == 42

    def test_foldL_sc(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii + jj

        def fold_is_lt42(d: int, fold_total: int) -> MB[int]:
            fold_total += d
            if fold_total < 42:
                return MB(fold_total)
            else:
                return MB()

        data1 = (1, 2, 3, 4, 5, None, 6, 7, 8, 9, 10)
        data2 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data3 = [1, 2, 3, 4, 5, 6]
        data4: tuple[int, ...] = ()
        data5 = 10,
        data6 = 15, 20, 25, 30

        assert foldL_sc(data1, add, pred=fold_is_lt42, istate=0) == 15
        assert foldL_sc(data2, add, pred=fold_is_lt42, istate=0) == 36
        assert foldL_sc(data3, add, pred=fold_is_lt42, istate=0) == 21
        assert foldL_sc(data4, add, pred=fold_is_lt42, istate=0) is None
        assert foldL_sc(data5, add, pred=fold_is_lt42, istate=0) == 10
        assert foldL_sc(data6, add, pred=fold_is_lt42, istate=0) == 35
        assert foldL_sc(data1, add, 10, pred=fold_is_lt42, istate=10) == 25
        assert foldL_sc(data2, add, 10, pred=fold_is_lt42, istate=10) == 38
        assert foldL_sc(data3, add, 20, pred=fold_is_lt42, istate=20) == 41
        assert foldL_sc(data4, add, 10, pred=fold_is_lt42, istate=10) == 10
        assert foldL_sc(data5, add, 10, pred=fold_is_lt42, istate=10) == 20
        assert foldL_sc(data6, add, 10, pred=fold_is_lt42, istate=10) == 25

    def test_foldR_sc(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii + jj

        def fold_is_lt42(d: int, fold_total: int) -> MB[int]:
            fold_total += d
            if fold_total < 42:
                return MB(fold_total)
            else:
                return MB()

        data1 = (1, 2, 3, 4, 5, -1, 6, 7, 8, 9, 10)
        data2 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data3 = [1, 2, 3, 4, 5, 6]
        data4: tuple[int, ...] = ()
        data5 = 10,
        data6 = 15, 20, 25, 30

        assert foldR_sc(data1, add, sent=-1, pred=fold_is_lt42, istate=0) == 15
        assert foldR_sc(data2, add, sent=-1, pred=fold_is_lt42, istate=0) == 36
        assert foldR_sc(data3, add, sent=-1, pred=fold_is_lt42, istate=0) == 21
        assert foldR_sc(data4, add, sent=-1, pred=fold_is_lt42, istate=0) == -1
        assert foldR_sc(data5, add, sent=-1, pred=fold_is_lt42, istate=0) == 10
        assert foldR_sc(data6, add, sent=-1, pred=fold_is_lt42, istate=0) == 35
        assert foldR_sc(data1, add, 10, sent=-1, pred=fold_is_lt42, istate=10) == 25
        assert foldR_sc(data2, add, 10, sent=-1, pred=fold_is_lt42, istate=10) == 38
        assert foldR_sc(data3, add, 20, sent=-1, pred=fold_is_lt42, istate=20) == 41
        assert foldR_sc(data4, add, 10, sent=-1, pred=fold_is_lt42, istate=10) == 10
        assert foldR_sc(data5, add, 10, sent=-1, pred=fold_is_lt42, istate=10) == 20
        assert foldR_sc(data6, add, 10, sent=-1, pred=fold_is_lt42, istate=10) == 25
