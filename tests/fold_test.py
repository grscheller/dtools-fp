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

from grscheller.fp.iterables import foldL, foldR
from grscheller.fp.nada import Nada, nada

class Test_fp_folds:
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

        assert foldL(data1, add) == 5050
        assert foldR(data1, add) == 5050
        assert foldL(data1, add, 10) == 5060
        assert foldR(data1, add, 10) == 5060

        assert foldL(data2, add) == 5049
        assert foldR(data2, add) == 5049
        assert foldL(data2, add, 10) == 5059
        assert foldR(data2, add, 10) == 5059

        assert foldL(data3, add) is nada
        assert foldR(data3, add) is nada
        assert foldL(data3, add, 10) == 10
        assert foldR(data3, add, 10) == 10

        assert foldL(data4, add) == 42
        assert foldR(data4, add) == 42
        assert foldL(data4, add, 10) == 52
        assert foldR(data4, add, 10) == 52

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert foldL(stuff1, add, default=None) == 15
        assert foldL(stuff1, add, None, default=None) == 15
        assert foldL(stuff1, add, 10, default=None) == 25
        assert foldR(stuff1, add, default=None) == 15
        assert foldL(stuff2, add, default=None) == 14
        assert foldR(stuff2, add, default=None) == 14
        assert foldL(stuff3, add, default=None) == None
        assert foldR(stuff3, add, default=None) == None
        assert foldL(stuff4, add, default=None) == 42
        assert foldR(stuff4, add, default=None) == 42
        assert foldL(stuff3, add, default=nada) is nada
        assert foldL(stuff3, add, default=nada) != nada
        assert foldL(stuff3, add) is nada
        assert foldR(stuff3, add) is nada
        assert foldL(stuff4, add) == 42
        assert foldR(stuff4, add) == 42

        assert foldL(stuff1, funcL, default=None) == -156
        assert foldR(stuff1, funcR, default=None) == 0
        assert foldL(stuff2, funcL, default=None) == 84
        assert foldR(stuff2, funcR, default=None) == 39
        assert foldL(stuff3, funcL, default=None) == None
        assert foldR(stuff3, funcR, default=None) == None
        assert foldL(stuff4, funcL, default=None) == 42
        assert foldR(stuff4, funcR, default=None) == 42
        assert foldL(stuff1, funcL) == -156
        assert foldR(stuff1, funcR) == 0
        assert foldL(stuff2, funcL) == 84
        assert foldR(stuff2, funcR) == 39
        assert foldL(stuff3, funcL) is nada
        assert foldR(stuff3, funcR) is nada
        assert foldL(stuff4, funcL) == 42
        assert foldR(stuff4, funcR) == 42

    def test_scfold(self) -> None:
        def add(ii: int|Nada, jj: int|Nada) -> int|Nada:
            if ii is nada or jj is nada:
                return -1
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

    #    assert sc_foldL(data1, add, nothing) == 15
    ##   assert sc_foldR(data1, add, nothing) == 15
    #    assert sc_foldL(data2, add, nothing) == 36
    ##   assert sc_foldR(data2, add, nothing) == 36
    #    assert sc_foldL(data3, add, nothing) == 21
    ##   assert sc_foldR(data3, add, nothing) == 21
    #    assert sc_foldL(data4, add, nothing) == nothing
    ##   assert sc_foldR(data4, add, nothing) == nothing
    #    assert sc_foldL(data5, add, nothing) == 10
    ##   assert sc_foldR(data5, add, nothing) == 10
    #    assert sc_foldL(data6, add, nothing) == 35
    ##   assert sc_foldR(data6, add, nothing) == 30
    #    assert sc_foldL(data1, add, nothing, 10) == 25
    ##   assert sc_foldR(data1, add, nothing, 10) == 25
    #    assert sc_foldL(data2, add, nothing, 10) == 38
    ##   assert sc_foldR(data2, add, nothing, 10) == 37
    #    assert sc_foldL(data3, add, nothing, 20) == 41
    ##   assert sc_foldR(data3, add, nothing, 20) == 39
    #    assert sc_foldL(data4, add, nothing, 10) == 10
    ##   assert sc_foldR(data4, add, nothing, 10) == 10
    #    assert sc_foldL(data5, add, nothing, 10) == 20
    ##   assert sc_foldR(data5, add, nothing, 10) == 20
    #    assert sc_foldL(data6, add, nothing, 10) == 25
    ##   assert sc_foldR(data6, add, nothing, 10) == 40


