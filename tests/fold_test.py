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

        assert foldL(data1, add2) == 5050
        assert foldR(data1, add2) == 5050
        assert foldL(data1, add2, 10) == 5060
        assert foldR(data1, add2, 10) == 5060

        assert foldL(data2, add2) == 5049
        assert foldR(data2, add2) == 5049
        assert foldL(data2, add2, 10) == 5059
        assert foldR(data2, add2, 10) == 5059

        assert foldL(data3, add2) is None
        assert foldR(data3, add2) is None
        assert foldL(data3, add2, 10) == 10
        assert foldR(data3, add2, 10) == 10

        assert foldL(data4, add2) == 42
        assert foldR(data4, add2) == 42
        assert foldL(data4, add2, 10) == 52
        assert foldR(data4, add2, 10) == 52

        stuff1 = (1, 2, 3, 4, 5)
        stuff2 = (2, 3, 4, 5)
        stuff3: list[int] = []
        stuff4 = 42,

        assert foldL(stuff1, add2) == 15
        assert foldR(stuff1, add2) == 15
        assert foldL(stuff1, add2, 10, 1000) == 25
        assert foldR(stuff1, add2) == 15
        assert foldL(stuff2, add2) == 14
        assert foldR(stuff2, add2) == 14
        assert foldL(stuff3, add2) == None
        assert foldR(stuff3, add2) == None
        assert foldL(stuff4, add2) == 42
        assert foldR(stuff4, add2) == 42
        assert foldL(stuff3, add2, sent=nada) is nada
        assert foldL(stuff3, add2, sent=1000) == 1000
        assert foldL(stuff3, add2) is None
        assert foldR(stuff3, add2) is None
        assert foldL(stuff4, add2) == 42
        assert foldR(stuff4, add2) == 42

        assert foldL(stuff1, funcL, sent=nada) == -156
        assert foldR(stuff1, funcR, sent=nada) == 0
        assert foldL(stuff2, funcL, sent=nada) == 84
        assert foldR(stuff2, funcR, sent=nada) == 39
        assert foldL(stuff3, funcL, sent=nada) is nada
        assert foldR(stuff3, funcR, sent=nada) is nada
        assert foldL(stuff4, funcL, sent=nada) == 42
        assert foldR(stuff4, funcR, sent=nada) == 42
        assert foldL(stuff1, funcL) == -156
        assert foldR(stuff1, funcR) == 0
        assert foldL(stuff2, funcL) == 84
        assert foldR(stuff2, funcR) == 39
        assert foldL(stuff3, funcL) is None
        assert foldR(stuff3, funcR) is None
        assert foldL(stuff4, funcL) == 42
        assert foldR(stuff4, funcR) == 42
