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

from grscheller.fp.iterators import concat, merge, exhaust

class Test_fp_iterators:
    def test_identity(self) -> None:
        ones = (1, 2, 3, 4, 5, 6, 7, 8, 9)
        tens = [10, 20, 30, 40, 50]
        hundreds = range(100, 800, 100)

        l_concat = list(concat(ones, tens, hundreds))
        l_merge = list(merge(ones, tens, hundreds))
        l_exhaust = list(exhaust(ones, tens, hundreds))

        assert len(l_concat) == 21
        assert len(l_merge) == 15
        assert len(l_exhaust) == 21

    def test_mixed_types(self) -> None:
        letters = 'abcdefghijklmnopqrstuvwxyz'

        mixed_tup_concat = tuple(concat(letters, range(10000)))
        mixed_tup_merge = tuple(merge(letters, range(10000)))
        mixed_tup_exhaust = tuple(exhaust(letters, range(10000)))

        assert len(mixed_tup_concat) == 10026
        assert len(mixed_tup_merge) == 52
        assert len(mixed_tup_exhaust) == 10026

        assert mixed_tup_concat[23:29] == ('x', 'y', 'z', 0, 1, 2)

        assert mixed_tup_merge[0:6] == ('a', 0, 'b', 1, 'c', 2)
        assert mixed_tup_merge[-6:] == ('x' ,23 ,'y', 24, 'z', 25)

        assert mixed_tup_exhaust[0:8] == ('a', 0, 'b', 1, 'c', 2, 'd', 3)
        assert mixed_tup_exhaust[46:54] == ('x', 23, 'y' ,24 ,'z', 25, 26, 27)

    def test_s(self) -> None:
        i0, i1, i2 = iter(['a0', 'b0', 'c0', 'd0', 'e0']), iter(['a1', 'b1', 'c1']), iter(['a2', 'b2', 'c2', 'd2', 'e2'])
        assert ('a0', 'a1', 'a2', 'b0', 'b1', 'b2', 'c0', 'c1', 'c2') == tuple(merge(i0, i1, i2))
        assert i0.__next__() == 'e0'        # 'd0' is lost!
        assert i2.__next__() == 'd2'
        assert i2.__next__() == 'e2'

        i0, i1, i2 = iter(['a0', 'b0', 'c0', 'd0', 'e0']), iter(['a1', 'b1', 'c1']), iter(['a2', 'b2', 'c2', 'd2', 'e2'])
        assert ('a0', 'a1', 'a2', 'b0', 'b1', 'b2', 'c0', 'c1', 'c2', 'd0') == tuple(merge(i0, i1, i2, yield_partial=True))
        assert i0.__next__() == 'e0'
        assert i2.__next__() == 'd2'
        assert i2.__next__() == 'e2'
