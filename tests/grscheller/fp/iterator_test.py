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

from grscheller.fp.iterables import concat, merge, exhaust
from grscheller.fp.iterables import accumulate

class Test_fp_iterables:
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

    def test_yield_partials(self) -> None:
        i0, i1, i2 = iter(['a0', 'b0', 'c0', 'd0', 'e0']), iter(['a1', 'b1', 'c1']), iter(['a2', 'b2', 'c2', 'd2', 'e2'])
        assert ('a0', 'a1', 'a2', 'b0', 'b1', 'b2', 'c0', 'c1', 'c2') == tuple(merge(i0, i1, i2))
        assert i0.__next__() == 'e0'        # 'd0' is lost!
        assert i2.__next__() == 'd2'
        assert i2.__next__() == 'e2'

        i0, i1, i2 = iter(['a0', 'b0', 'c0', 'd0', 'e0']), iter(['a1', 'b1', 'c1']), iter(['a2', 'b2', 'c2', 'd2', 'e2'])
        assert ('a0', 'a1', 'a2', 'b0', 'b1', 'b2', 'c0', 'c1', 'c2', 'd0') == tuple(merge(i0, i1, i2, yield_partials=True))
        assert i0.__next__() == 'e0'
        assert i2.__next__() == 'd2'
        assert i2.__next__() == 'e2'

    def test_merges_concats(self) -> None:
        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(concat(i3, i0, i4))) == 7
        assert tup == ('a3', 'b3', 'c3', 'a4', 'b4', 'c4', 'd4')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(concat(i0, i3, i4))) == 7
        assert tup == ('a3', 'b3', 'c3', 'a4', 'b4', 'c4', 'd4')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(concat(i4, i3, i0))) == 7
        assert tup == ('a4', 'b4', 'c4', 'd4', 'a3', 'b3', 'c3')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(exhaust(i3, i0, i4))) == 7
        assert tup == ('a3', 'a4', 'b3', 'b4', 'c3', 'c4', 'd4')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(exhaust(i0, i3, i4))) == 7
        assert tup == ('a3', 'a4', 'b3', 'b4', 'c3', 'c4', 'd4')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(exhaust(i4, i3, i0))) == 7
        assert tup == ('a4', 'a3', 'b4', 'b3', 'c4', 'c3', 'd4')

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i3, i0, i4))) == 0
        assert tup == ()

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i0, i3, i4))) == 0
        assert tup == ()

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i4, i3, i0))) == 0
        assert tup == ()

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i3, i0, i4, yield_partials=True))) == 1
        assert tup == ('a3',)

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i0, i3, i4, yield_partials=True))) == 0
        assert tup == ()

        i3, i0, i4 = iter(('a3', 'b3', 'c3')), iter(()), iter(('a4', 'b4', 'c4', 'd4'))
        assert len(tup := tuple(merge(i4, i3, i0, yield_partials=True))) == 2
        assert tup == ('a4', 'a3')

    def test_mixed_cases(self) -> None:
        i3, ih, i4 = iter(('a3', 'b3', 'c3')), iter('hello'), iter([1, 2, 3, 4])
        assert len(tup1 := tuple(concat(i3, ih, i4))) == 12
        assert tup1 == ('a3', 'b3', 'c3', 'h', 'e', 'l', 'l', 'o', 1, 2, 3, 4)

        i3, ih, i4 = iter(('a3', 'b3', 'c3')), iter('hello'), iter([1, 2, 3, 4])
        tup2: tuple[int|str, ...] = tuple(concat(i3, ih, i4))
        assert len(tup2) == 12
        assert tup2 == ('a3', 'b3', 'c3', 'h', 'e', 'l', 'l', 'o', 1, 2, 3, 4)

    def test_accumulate(self) -> None:
        def add(x: int, y: int) -> int:
            return x+y

        def addPlusOne(x: int, y: int) -> int:
            return x+y+1

        foo: list[int] = [5,4,3,2,1]
        fooPlusOne = list(accumulate(foo, addPlusOne, 10))
        fooPlus = list(accumulate(foo, add))
        fooMult = list(accumulate(foo, lambda a,b: a*b))
        assert fooPlus == [5, 9, 12, 14, 15]
        assert fooMult == [5, 20, 60, 120, 120]

        bar: list[int] = []
        barPlus = list(accumulate(bar, add))
        assert barPlus == []
        barPlus = list(accumulate(bar, add, 0))
        barMult = list(accumulate(bar, lambda a,b: a*b, 1))
        assert barPlus == [0]
        assert barMult == [1]

        woo: list[int] = [5,4,3,2,1]
        wooPlus1 = list(accumulate(woo, add, initial=1))
        wooMult1 = list(accumulate(woo, lambda a,b: a*b, initial=10))
        assert wooPlus1 == [1, 6, 10, 13, 15, 16]
        assert wooMult1 == [10, 50, 200, 600, 1200, 1200]
        nowooPlus1 = list(accumulate([], add, initial=1))
        nowooMult1 = list(accumulate([], lambda a,b: a*b, 10))
        assert nowooPlus1 == [1]
        assert nowooMult1 == [10]

        baz: list[int] = []
        bazPlus = list(accumulate(baz, addPlusOne, 1))
        bazMult = list(accumulate(baz, lambda a,b: a*b, 10))
        assert bazPlus == [1]
        assert bazMult == [10]
        bazPlus = list(accumulate(baz, addPlusOne))
        assert bazPlus == []

        bat = (5,4,3,2,1)
        empty: tuple[int, ...] = ()
        batPlus = list(accumulate(bat, lambda t,i: (i,) + t, empty))
        assert batPlus == [(), (5,), (4, 5), (3, 4, 5), (2, 3, 4, 5), (1, 2, 3, 4, 5)]

