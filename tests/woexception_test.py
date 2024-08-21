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

from __future__ import annotations

from typing import Optional
from grscheller.fp.woException import MB, XOR, mb_to_xor, xor_to_mb
from grscheller.fp.nada import Nada, nada

def add2(x: int) -> int:
    return x + 2

class TestMB:
    def test_identity(self) -> None:
        n1: MB[int] = MB()
        n2: MB[int] = MB()
        o1 = MB(42)
        o2 = MB(40)
        assert o1 is o1
        assert o1 is not o2
        o3 = o2.map(add2)
        assert o3 is not o2
        assert o1 is not o3
        assert n1 is n1
        assert n1 is not n2
        assert o1 is not n1
        assert n2 is not o2

    def test_equality(self) -> None:
        n1: MB[int] = MB()
        n2: MB[int] = MB()
        o1 = MB(42)
        o2 = MB(40)
        assert o1 == o1
        assert o1 != o2
        o3 = o2.map(add2)
        assert o3 != o2
        assert o1 == o3
        assert n1 == n1
        assert n1 == n2
        assert o1 != n1
        assert n2 != o2

    def test_iterate(self) -> None:
        o1 = MB(38)
        o2 = o1.map(add2).map(add2)
        n1: MB[int] = MB()
        l1 = []
        l2 = []
        for v in n1:
            l1.append(v)
        for v in o2:
            l2.append(v)
        assert len(l1) == 0
        assert len(l2) == 1
        assert l2[0] == 42

    def test_get(self) -> None:
        o1 = MB(1)
        n1: MB[int] = MB()
        assert o1.get(42) == 1
        assert n1.get(21) == 21
        assert o1.get() == 1
        try:
            foo = 42
            foo = n1.get()
        except ValueError:
            assert True
        else:
            assert False
        finally:
            assert foo == 42
        assert n1.get(13) == (10 + 3)
        assert n1.get(10//7) == 10//7

    def test_equal_self(self) -> None:
        mb42 = MB(40+2)
        mbno: MB[int] = MB()
        mb42 != mbno
        mb42 == mb42
        mbno == mbno

def gt42(x: int) -> bool|Nada:
    if x > 42:
        return True
    if x == 42:
        return False
    return nada

class TestXOR:
    def test_equal_self(self) -> None:
        xor42 = XOR(40+2, 'forty-two')
        xorno42: XOR[int, str] = XOR(right='no forty-two')
        xor_fortytwo = XOR('forty-two', 21*2)
        xor42tuple = XOR(42, (2, 3))

        assert xor42 == xor42
        assert xorno42 == xorno42
        assert xor_fortytwo == xor_fortytwo
        assert xor42tuple == xor42tuple

        assert xor42 != xor_fortytwo
        assert xor42 == xor42tuple

        xor42 = xor42.mapRight(lambda _: 'none')
        thing1: XOR[int, str] = xor42.mapRight(lambda s: s + '?').makeRight()
        thing2: XOR[int, str] = xor42.flatMap(lambda _: XOR(right='none?'))
        assert thing1 == thing2

        xor_99 = XOR(99, 'orig 99')
        xor_86 = XOR(86, 'orig 86')
        xor_42 = XOR(42, 'orig 42')
        xor_21 = XOR(21, 'orig 21')
        xor_12 = XOR(12, 'orig 12')

        assert xor_99.map(gt42) == xor_86.map(gt42)
        assert xor_21.map(gt42) != xor_12.map(gt42)
        assert xor_21.map(gt42).swapRight('lt 42') == xor_12.map(gt42).swapRight('lt 42')

        hymie = xor_86.map(gt42).mapRight(lambda s: f'Hymie says: {s}')
        chief = xor_86.map(gt42).mapRight(lambda s: f'Chief says: {s}')
        ratton = xor_21.map(gt42).mapRight(lambda s: f'Dr. Ratton says: {s}')
        seigfried = xor_21.map(gt42).mapRight(lambda s: f'Seigfried says: {s}')

        assert hymie == chief
        assert ratton != seigfried

        assert repr(hymie) == "XOR(True, 'Hymie says: orig 86')"
        assert repr(chief) == "XOR(True, 'Chief says: orig 86')"
        assert repr(ratton) == "XOR(nada, 'Dr. Ratton says: orig 21')"
        assert repr(seigfried) == "XOR(nada, 'Seigfried says: orig 21')"

        assert xor_12.map(gt42).swapRight('not greater than 42') == XOR(right='not greater than 42')

    def test_identity(self) -> None:
        e1: XOR[int, str] = XOR(42, '')
        e2: XOR[int, str] = XOR(42, '')
        e3: XOR[int, str] = XOR(42, 'The secret is unknown')
        e4: XOR[int, str] = XOR(nada, 'not 42')
        e5: XOR[int, str] = XOR(nada, 'also not 42')
        e6 = e3
        assert e1 is e1
        assert e1 is not e2
        assert e1 is not e3
        assert e1 is not e4
        assert e1 is not e5
        assert e1 is not e6
        assert e2 is e2
        assert e2 is not e3
        assert e2 is not e4
        assert e2 is not e5
        assert e2 is not e6
        assert e3 is e3
        assert e3 is not e4
        assert e3 is not e5
        assert e3 is e6
        assert e4 is e4
        assert e4 is not e5
        assert e4 is not e6
        assert e5 is e5
        assert e5 is not e6
        assert e6 is e6

    def test_equality(self) -> None:
        nono = Nada()
        e1: XOR[int, str] = XOR(42, '')
        e2: XOR[int, str] = XOR(42, '')
        e3: XOR[int, str] = XOR(nono, 'not 42')
        e4: XOR[int, str] = XOR(nono, 'not 42')
        e5: XOR[int, str] = XOR(nono, 'also not 42')
        e6 = e3
        assert e1 == e1
        assert e1 == e2
        assert e1 != e3
        assert e1 != e4
        assert e1 != e5
        assert e1 != e6
        assert e2 == e2
        assert e2 != e3
        assert e2 != e4
        assert e2 != e5
        assert e2 != e6
        assert e3 == e3
        assert e3 == e4
        assert e3 != e5
        assert e3 == e6
        assert e4 == e4
        assert e4 != e5
        assert e4 == e6
        assert e5 == e5
        assert e5 != e6
        assert e6 == e6

    def test_either_right(self) -> None:
        def noMoreThan5(x: int) -> int|Nada:
            if x <= 5:
                return x
            else:
                return Nada()

        s1 = XOR(3, right = 'foofoo rules')
        s2 = s1.map(noMoreThan5).mapRight(lambda _: 'more than 5')
        s3 = XOR(42, 'foofoo rules')
        s4 = s3.map(noMoreThan5).mapRight(lambda _: 'more than 5')
        assert s1.get() == 3
        assert s2.get() == 3
        assert s4.get(42) == 42
        bar = 'barbell'
        bar = s1.getRight()
        assert bar == 'foofoo rules'
        assert s2.getRight('everything OK') == 'everything OK'
        assert s3.getRight('no rights here') == 'no rights here'
        assert s4.getRight() == 'more than 5'
        assert s1.get(0) == 3
        assert s3.get(0) == 42
        assert s4.get(0) == 0
        assert s4.getRight() == 'more than 5'

    def test_either_flatMaps(self) -> None:
        def lessThan2(x: int) -> XOR[int, str]:
            if x < 2:
                return XOR(x, 'fail!')
            else:
                return XOR(Nada(), '>=2')

        def lessThan5(x: int) -> XOR[int, str]:
            if x < 5:
                return XOR(x, '')
            else:
                return XOR(Nada(), '>=5')

        left1 = XOR(1, 'no')
        left4 = XOR(4, '')
        left7 = XOR(7, 'foobar')
        right: XOR[int, str] = XOR(Nada(), 'Nobody home')

        nobody = right.flatMap(lessThan2)
        assert nobody == XOR(Nada(), 'Nobody home')

        lt2 = left1.flatMap(lessThan2)
        lt5 = left1.flatMap(lessThan5)
        assert lt2 == XOR(1, 'foofoo rules')
        assert lt5 == XOR(1, '')

        lt2 = left4.flatMap(lessThan2)
        lt5 = left4.flatMap(lessThan5)
        assert lt2 == XOR(Nada(), '>=2')
        assert lt5 == XOR(4, '>=5')

        lt2 = left7.flatMap(lessThan2)
        lt5 = left7.flatMap(lessThan5)
        assert lt2 == XOR(Nada(), '>=2')
        assert lt5 == XOR(Nada(), '>=5')

        nobody = right.flatMap(lessThan5)
        assert nobody == XOR(Nada(), 'Nobody home')

        lt2 = left1.flatMap(lessThan2)
        lt5 = left1.flatMap(lessThan5)
        assert lt2 == XOR(1,'not me')
        assert lt5 == XOR(1, 'not me too')

        lt2 = left4.flatMap(lessThan2)
        lt5 = left4.flatMap(lessThan5)
        assert lt2 == XOR(Nada(), '>=2')
        assert lt2 != XOR(42, '>=42')
        assert lt5 == XOR(4, 'boo')
        assert lt5 != XOR(42, 'boohoo')

        lt2 = left7.flatMap(lessThan2).mapRight(lambda _: 'greater than or equal 2')
        lt5 = left7.flatMap(lessThan5).mapRight(lambda s: s + ', greater than or equal 5')
        assert lt2 == XOR(Nada(), 'greater than or equal 2')
        assert lt5 == XOR(Nada(), '>=5, greater than or equal 5')

    def test_MB_XOR(self) -> None:
        mb42 = MB(42)
        mbNot: MB[int] = MB()

        left42 = mb_to_xor(mb42, 'fail!')
        right = mb_to_xor(mbNot, 'Nobody home')
        assert left42 == XOR(42, 'fail!')
        assert right == XOR(nada, 'Nobody home')

        ph42 = xor_to_mb(left42)
        phNot = xor_to_mb(right)
        assert mb42 == ph42
        assert mbNot == phNot
