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
from dtools.fp.iterables import reducel, foldl, mb_fold_left, scReducel, scReducer
from dtools.fp.err_handling import MB
from dtools.fp.function import swap, partial

add: Callable[[int, int], int] = lambda a, b: a+b

def ge_n(a: int, n: int) -> bool:
    return a >= n

def le_n(a: int, n: int) -> bool:
    return a <= n

class Test_fp_folds:
    def test_fold_comuinitive(self) -> None:
        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert reducel(data1, add) == 5050
        assert foldl(data1, add, 10) == 5060

        assert reducel(data2, add) == 5049
        assert foldl(data2, add, 10) == 5059

        assert foldl(data3, add, 0) == 0
        assert foldl(data3, add, 10) == 10

        assert reducel(data4, add) == 42
        assert foldl(data4, add, 10) == 52

        data1 = (1, 2, 3, 4, 5)
        data2 = (2, 3, 4, 5)
        data5: list[int] = []

        assert reducel(data1, add) == 15
        assert foldl(data1, add, 10) == 25
        assert reducel(data2, add) == 14
        assert reducel(data4, add) == 42
        assert reducel(data4, add) == 42
        assert foldl(data5, add, 0) == 0
        assert foldl(data5, add, -42) == -42

    def test_fold_noncomuinitive(self) -> None:
        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = (1, 2, 3, 4, 5)
        data2 = (2, 3, 4, 5)
        data3: list[int] = []
        data4 = 42,

        assert reducel(data1, funcL) == -156
        assert reducel(data2, funcL) == 84
        assert foldl(data3, funcL, 0) == 0
        assert foldl(data3, funcL, -1) == -1
        assert reducel(data4, funcL) == 42
        assert reducel(data1, funcL) == -156
        assert reducel(data2, funcL) == 84
        assert reducel(data2, funcL) == 84

class Test_fp_mbFolds:
    def test_mbFold(self) -> None:
        def funcL(acc: int, jj: int) -> int:
            return (acc - 1)*(jj + 1)

        def funcR(ii: int, acc: int) -> int:
            return (ii - 1)*(acc + 1)

        data1 = tuple(range(1, 101))
        data2 = tuple(range(2, 101))
        data3: tuple[int, ...] = ()
        data4 = 42,

        assert mb_fold_left(data1, add) == MB(5050)
        assert mb_fold_left(data1, add, 10) == MB(5060)

        assert mb_fold_left(data2, add) == MB(5049)
        assert mb_fold_left(data2, add, 10) == MB(5059)

        assert mb_fold_left(data3, add) == MB()
        assert mb_fold_left(data3, add, 10) == MB(10)

        assert mb_fold_left(data4, add) == MB(42)
        assert mb_fold_left(data4, add, 10) == MB(52)

        data1 = (1, 2, 3, 4, 5)
        data2 = (2, 3, 4, 5)
        data3: list[int] = []
        data4 = 42,

        assert mb_fold_left(data1, add) == MB(15)
        assert mb_fold_left(data1, add, 10) == MB(25)
        assert mb_fold_left(data2, add) == MB(14)
        assert mb_fold_left(data3, add) == MB()
        assert mb_fold_left(data4, add) == MB(42)
        assert mb_fold_left(data4, add).get(-1) == 42
        assert mb_fold_left(data3, add).get(-1) == -1

        assert mb_fold_left(data1, funcL) == MB(-156)
        assert mb_fold_left(data2, funcL) == MB(84)
        assert mb_fold_left(data3, funcL) == MB()
        assert mb_fold_left(data3, funcL).get(-1) == -1
        assert mb_fold_left(data4, funcL) == MB(42)
        assert mb_fold_left(data1, funcL) == MB(-156)
        assert mb_fold_left(data2, funcL) == MB(84)
        assert mb_fold_left(data2, funcL).get() == 84

class Test_fp_scReduceL:

    def test_defaults(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        mb_sum55, it = scReducel(data, add)
        try:
            next(it)
        except StopIteration:
            assert mb_sum55 == MB(55)
        else:
            assert False

    def test_start_stop(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        ge2 = partial(swap(ge_n), 2)
        ge8 = partial(swap(ge_n), 8)

        mb_sum35, it = scReducel(data, add, start=ge2, stop=ge8)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int9, mb_sum35) == (9, MB(35))

        mb_sum33, it = scReducel(data, add, start=ge2, stop=ge8,
                                 include_start=False)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int9, mb_sum33) == (9, MB(33))

        mb_sum27, it = scReducel(data, add, start=ge2, stop=ge8,
                                 include_stop=False)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int8, MB(mb_sum27)) == (8, MB(27))

        # ---------------------------------------------------------------

        mb_sum8, it = scReducel(data, add, start=ge8, stop=ge2)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int9, mb_sum8) == (9, MB(8))

        mb_sum9, it = scReducel(data, add, start=ge8, stop=ge2,
                                include_start=False)
        try:
            int10 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int10, mb_sum9) == (10, MB(9))

        mb_empty, it = scReducel(data, add, start=ge8, stop=ge2,
                                 include_stop=False)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int8, mb_empty) == (8, MB())

        mb_empty, it = scReducel(data, add, start=ge8, stop=ge2,
                                 include_start=False, include_stop=False)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int9, mb_empty) == (9, MB())

class Test_fp_scReduceR:

    def test_defaults(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        mb_sum55, it = scReducer(data, add)
        try:
            next(it)
        except StopIteration:
            assert True
        else:
            assert False
        assert mb_sum55 == MB(55)

    def test_start_stop(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        ge7 = partial(swap(ge_n), 7)
        le4 = partial(swap(le_n), 4)

        mb_sum22, it = scReducer(data, add, start=ge7, stop=le4)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int8, mb_sum22) == (8, MB(22))

        mb_sum15, it = scReducer(data, add, start=ge7, stop=le4,
                                 include_start=False)
        try:
            int7 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int7, mb_sum15) == (7, MB(15))

        mb_sum18, it = scReducer(data, add, start=ge7, stop=le4,
                                 include_stop=False)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int8, mb_sum18) == (8, MB(18))

        mb_sum11, it = scReducer(data, add, start=ge7, stop=le4,
                                 include_start=False, include_stop=False)
        try:
            int7 = next(it)
        except StopIteration:
            assert False
        else:
            assert (int7, mb_sum11) == (7, MB(11))


    def test_start_stop_edge_case_all(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        ge10 = partial(swap(ge_n), 10)
        le1 = partial(swap(le_n), 1)

        mb_sum55, it = scReducer(data, add, start=ge10, stop=le1)
        try:
            next(it)
        except StopIteration:
            assert True
        assert mb_sum55 == MB(55)

        mb_sum44, it = scReducer(data, add, start=ge10, stop=le1,
                                 include_start=False, include_stop=False)
        try:
            int10 = next(it)
        except StopIteration:
            assert False
        finally:
            assert (int10, mb_sum44) == (10, MB(44))

        mb_sum45, it = scReducer(data, add, start=ge10, stop=le1,
                                 include_start=False)
        try:
            int10 = next(it)
        except StopIteration:
            assert False
        assert (int10, mb_sum45) == (10, MB(45))

        mb_sum54, it = scReducer(data, add, start=ge10, stop=le1,
                                 include_stop=False)
        try:
            int10 = next(it)
        except StopIteration:
            assert True
        assert mb_sum54 == MB(54)

    def test_start_stop_edge_case_next_to(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

        ge8 = partial(swap(ge_n), 8)
        le7 = partial(swap(le_n), 7)

        mb_sum15, it = scReducer(data, add, start=ge8, stop=le7)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        assert (int9, mb_sum15) == (9, MB(15))

    def test_start_stop_edge_case_same(self) -> None:
        data = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

        ge8 = partial(swap(ge_n), 8)
        le8 = partial(swap(le_n), 8)

        mb_sum8, it = scReducer(data, add, start=ge8, stop=le8)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        assert (int9, mb_sum8) == (9, MB(8))

        # ---------------------------------------------------------------

        mb_empty, it = scReducer(data, add, start=ge8, stop=le8,
                                 include_start=False, include_stop=False)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        assert (int8, mb_empty) == (8, MB())

        # ---------------------------------------------------------------

        mb_empty, it = scReducer(data, add, start=ge8, stop=le8,
                                 include_stop=False)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        assert (int9, mb_empty) == (9, MB())

        le7 = partial(swap(le_n), 7)

        mb_sum8, it = scReducer(data, add, start=ge8, stop=le7,
                                 include_stop=False)
        try:
            int9 = next(it)
        except StopIteration:
            assert False
        assert (int9, mb_sum8) == (9, MB(8))

        mb_empty, it = scReducer(data, add, start=ge8, stop=le7,
                                 include_start=False, include_stop=False)
        try:
            int8 = next(it)
        except StopIteration:
            assert False
        assert (int8, mb_empty) == (8, MB())

        # ---------------------------------------------------------------

