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

from grscheller.fp.iterators import foldL, foldR, sc_foldL
from grscheller.fp.nothing import nothing, Nothing

class Test_fp_folds:
    def test_fold(self) -> None:
        def add(ii: int, jj: int) -> int:
            return ii+jj

        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = (1, 2, 3, 4, 5)
        data2 = (2, 3, 4, 5)
        data3: list[int] = []
        data4 = 42,

        assert foldL(data1, add, None) == 15
        assert foldR(data1, add, None) == 15
        assert foldL(data2, add, None) == 14
        assert foldR(data2, add, None) == 14
        assert foldL(data3, add, None) == None
        assert foldR(data3, add, None) == None
        assert foldL(data4, add, None) == 42
        assert foldR(data4, add, None) == 42
        assert foldL(data3, add, nothing) == nothing
        assert foldR(data3, add, nothing) == nothing
        assert foldL(data4, add, nothing) == 42
        assert foldR(data4, add, nothing) == 42
        assert foldL(data4, add, nothing) == 42
        assert foldR(data4, add, nothing) == 42


        assert foldL(data1, funcL, None) == -156
        assert foldR(data1, funcR, None) == 0
        assert foldL(data2, funcL, None) == 84
        assert foldR(data2, funcR, None) == 39
        assert foldL(data3, funcL, None) == None
        assert foldR(data3, funcR, None) == None
        assert foldL(data4, funcL, None) == 42
        assert foldR(data4, funcR, None) == 42
        assert foldL(data1, funcL, nothing) == -156
        assert foldR(data1, funcR, nothing) == 0
        assert foldL(data2, funcL, nothing) == 84
        assert foldR(data2, funcR, nothing) == 39
        assert foldL(data3, funcL, nothing) == nothing
        assert foldR(data3, funcR, nothing) == nothing
        assert foldL(data4, funcL, nothing) == 42
        assert foldR(data4, funcR, nothing) == 42

    def test_scfold(self) -> None:
        def add(ii: int|Nothing, jj: int|Nothing) -> int|Nothing:
            if ii is nothing or jj is nothing:
                return -1
            if (kk := ii+jj) < 42:
                return kk
            else:
                return nothing

        data1 = (1, 2, 3, 4, 5, nothing, 6, 7, 8, 9, 10)
        data2 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data3 = [1, 2, 3, 4, 5, 6]
        data4: tuple[int, ...] = ()
        data5 = 10,
        data6 = 15, 20, 25, 30

        assert sc_foldL(data1, add, nothing) == 15
    #   assert sc_foldR(data1, add, nothing) == 15
        assert sc_foldL(data2, add, nothing) == 36
    #   assert sc_foldR(data2, add, nothing) == 36
        assert sc_foldL(data3, add, nothing) == 21
    #   assert sc_foldR(data3, add, nothing) == 21
        assert sc_foldL(data4, add, nothing) == nothing
    #   assert sc_foldR(data4, add, nothing) == nothing
        assert sc_foldL(data5, add, nothing) == 10
    #   assert sc_foldR(data5, add, nothing) == 10
        assert sc_foldL(data6, add, nothing) == 35
    #   assert sc_foldR(data6, add, nothing) == 30
        assert sc_foldL(data1, add, nothing, 10) == 25
    #   assert sc_foldR(data1, add, nothing, 10) == 25
        assert sc_foldL(data2, add, nothing, 10) == 38
    #   assert sc_foldR(data2, add, nothing, 10) == 37
        assert sc_foldL(data3, add, nothing, 20) == 41
    #   assert sc_foldR(data3, add, nothing, 20) == 39
        assert sc_foldL(data4, add, nothing, 10) == 10
    #   assert sc_foldR(data4, add, nothing, 10) == 10
        assert sc_foldL(data5, add, nothing, 10) == 20
    #   assert sc_foldR(data5, add, nothing, 10) == 20
        assert sc_foldL(data6, add, nothing, 10) == 25
    #   assert sc_foldR(data6, add, nothing, 10) == 40


