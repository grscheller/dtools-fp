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

from grscheller.fp.iterables import foldL_sc, foldR_sc
from grscheller.fp.nada import Nada, nada

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

        assert foldL_sc(stuff1, add, sentinel=None) == 15
        assert foldL_sc(stuff1, add, None, sentinel=None) == 15
        assert foldL_sc(stuff1, add, 10, sentinel=None) == 25
        # assert foldR_sc(stuff1, add, sentinel=None) == 15
        assert foldL_sc(stuff2, add, sentinel=None) == 14
        # assert foldR_sc(stuff2, add, sentinel=None) == 14
        assert foldL_sc(stuff3, add, sentinel=None) == None
        # assert foldR_sc(stuff3, add, sentinel=None) == None
        assert foldL_sc(stuff4, add, sentinel=None) == 42
        # assert foldR_sc(stuff4, add, sentinel=None) == 42
        assert foldL_sc(stuff3, add, sentinel=nada) is nada
        assert foldL_sc(stuff3, add, sentinel=nada) != nada
        assert foldL_sc(stuff3, add) is None
        assert foldR_sc(stuff3, add) is None
        assert foldL_sc(stuff4, add) == 42
        assert foldR_sc(stuff4, add) == 42

        assert foldL_sc(stuff1, funcL, sentinel=nada) == -156
        assert foldR_sc(stuff1, funcR, sentinel=nada) == 0
        assert foldL_sc(stuff2, funcL, sentinel=nada) == 84
        assert foldR_sc(stuff2, funcR, sentinel=nada) == 39
        assert foldL_sc(stuff3, funcL, sentinel=nada) is nada
        assert foldR_sc(stuff3, funcR, sentinel=nada) is nada
        assert foldL_sc(stuff4, funcL) == 42
        assert foldR_sc(stuff4, funcR, sentinel=nada) == 42
        assert foldL_sc(stuff1, funcL) == -156
        assert foldR_sc(stuff1, funcR) == 0
        assert foldL_sc(stuff2, funcL) == 84
        assert foldR_sc(stuff2, funcR) == 39
        assert foldL_sc(stuff3, funcL) is None
        assert foldR_sc(stuff3, funcR) is None
        assert foldL_sc(stuff4, funcL) == 42
        assert foldR_sc(stuff4, funcR) == 42

    def test_fold_sc(self) -> None:
        def add2(ii: int, jj: int) -> int|Nada:
            if (kk := ii+jj) < 42:
                return kk
            else:
                return nada

        data1 = (1, 2, 3, 4, 5, nada, 6, 7, 8, 9, 10)
        data2 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data3 = [1, 2, 3, 4, 5, 6]
        data4: tuple[int, ...] = ()
        data5 = 10,
        data6 = 15, 20, 25, 30

        assert foldL_sc(data1, add2, sentinel=nada) == 15
    #   assert foldR_sc(data1, add2, sentinel=nada) == 15
        assert foldL_sc(data2, add2, sentinel=nada) == 36
    #   assert foldR_sc(data2, add2, sentinel=nada) == 36
        assert foldL_sc(data3, add2, sentinel=nada) == 21
    #   assert foldR_sc(data3, add2, sentinel=nada) == 21
        assert foldL_sc(data4, add2, sentinel=nada) is nada
    #   assert foldR_sc(data4, add2, sentinel=nada) == nada
        assert foldL_sc(data5, add2, sentinel=nada) == 10
    #   assert foldR_sc(data5, add2, sentinel=nada) == 10
        assert foldL_sc(data6, add2, sentinel=nada) == 35
    #   assert foldR_sc(data6, add2, sentinel=nada) == 30
        assert foldL_sc(data1, add2, 10, sentinel=nada) == 25
    #   assert foldR_sc(data1, add2, sentinel=nada, 10) == 25
        assert foldL_sc(data2, add2, 10, sentinel=nada) == 38
    #   assert foldR_sc(data2, add2, sentinel=nada, 10) == 37
        assert foldL_sc(data3, add2, 20, sentinel=nada) == 41
    #   assert foldR_sc(data3, add2, sentinel=nada, 20) == 39
        assert foldL_sc(data4, add2, 10, sentinel=nada) == 10
    #   assert foldR_sc(data4, add2, sentinel=nada, 10) == 10
        assert foldL_sc(data5, add2, 10, sentinel=nada) == 20
    #   assert foldR_sc(data5, add2, sentinel=nada, 10) == 20
        assert foldL_sc(data6, add2, 10, sentinel=nada) == 25
    #   assert foldR_sc(data6, add2, sentinel=nada, 10) == 40


