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

from __future__ import annotations

from dtools.tuples.ftuple import f_tuple as ft
from dtools.fp.err_handling import MB, XOR

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

def gt42(x: int) -> MB[bool]:
    if x > 42:
        return MB(True)
    if x == 42:
        return MB(False)
    return MB()

def lt42(x: int) -> XOR[bool, str]:
    if x < 42:
        return XOR(True, str(x))
    if x == 42:
        return XOR(False, str(x))
    return XOR(MB(), str(x))

class TestXOR:
    def test_equal_self(self) -> None:
        xor41 = XOR(40+1, '41')
        xor42 = XOR(40+2, '42')
        xor43 = XOR(40+3, '43')
        xorno42: XOR[int, str] = XOR(MB(), 'no 42')
        xor_fortytwo = XOR('forty-two', 21*2)
        xor42tuple = XOR(42, (2, 3))

        assert xor42 == xor42
        assert xorno42 == xorno42
        assert xor_fortytwo == xor_fortytwo
        assert xor42tuple == xor42tuple

        assert xor41 != xor43
        assert xor42 != xor_fortytwo
        assert xor42 == xor42tuple

        xor_42 = xor42.mapRight(lambda _: 'none', 'mapRight failed')
        thing1: XOR[int, str] = xor_42.mapRight((lambda s: s + '?'), 'Not sure if I need this.').makeRight()
        thing2: XOR[int, str] = xor_42.bind(lambda _: XOR(MB(), 'none?'))
        assert thing1 == thing2

        ft_xor_int_str = ft(xor41, xor42, xor43)
        ft_xor_bool_str = ft_xor_int_str.map(lambda x: x.bind(lt42))

        assert ft_xor_bool_str[0] == XOR(True, '41')
        assert ft_xor_bool_str[1] == XOR(False, 'does not matter what we put here')
        assert ft_xor_bool_str[2] == XOR(MB(), '43')

        ft_xor_bool_str_right = ft_xor_bool_str.map(lambda x: x.makeRight())

        assert ft_xor_bool_str_right[0] == XOR(MB(), '41')
        assert ft_xor_bool_str_right[1] == XOR(MB(), '42')
        assert ft_xor_bool_str_right[2] == XOR(MB(), '43')

        xor_99 = XOR(99, 'orig 99')
        xor_86 = XOR(86, 'orig 86')
        xor_42 = XOR(42, 'orig 42')
        xor_21 = XOR(21, 'orig 21')
        xor_12 = XOR(12, 'orig 12')

        assert xor_99.map(gt42) == xor_86.map(gt42)
        assert xor_21.map(gt42) != xor_12.map(gt42)
        assert xor_21.map(gt42).newRight('lt 42') == xor_12.map(gt42).newRight('lt 42')

        hymie = xor_86.map(gt42).mapRight((lambda s: f'Hymie says: {s}'), 'got some oil?')
        chief = xor_86.map(gt42).mapRight((lambda s: f'Chief says: {s}'), 'not the dome of silence!')
        ratton = xor_21.map(gt42).mapRight((lambda s: f'Dr. Ratton says: {s}'), 'where is hymie?')
        seigfried_lambda = lambda s: f'Seigfried says: {s}'
        seigfried_secret_headquarters = 'somewhere in NJ'
        seigfried = xor_21.map(gt42).mapRight(seigfried_lambda, seigfried_secret_headquarters)

        assert hymie == chief
        assert ratton != seigfried

        assert repr(hymie) == "XOR(True, 'Hymie says: orig 86')"
        assert repr(chief) == "XOR(True, 'Chief says: orig 86')"
        assert repr(ratton) == "XOR(MB(), 'Dr. Ratton says: orig 21')"
        assert repr(seigfried) == "XOR(MB(), 'Seigfried says: orig 21')"

        assert xor_12.map(gt42).newRight('not greater than 42') == XOR(MB(), 'not greater than 42')

    def test_identity(self) -> None:
        e1: XOR[int, str] = XOR(42, '')
        e2: XOR[int, str] = XOR(42, '')
        e3: XOR[int, str] = XOR(42, 'The secret is unknown')
        e4: XOR[int, str] = XOR(MB(), 'not 42')
        e5: XOR[int, str] = XOR(MB(), 'also not 42')
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
        e1: XOR[int, str] = XOR(42, '')
        e2: XOR[int, str] = XOR(42, '')
        e3: XOR[int, str] = XOR(MB(), 'not 42')
        e4: XOR[int, str] = XOR(MB(), 'not 42')
        e5: XOR[int, str] = XOR(MB(), 'also not 42')
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
        def noMoreThan5(x: int) -> MB[int]:
            if x <= 5:
                return MB(x)
            else:
                return MB()

        s1 = XOR(3, 'foofoo rules')
        s2 = s1.map(noMoreThan5).mapRight((lambda _: 'more than 5'), 'failed')
        s3 = XOR(42, 'foofoo rules')
        s4 = s3.map(noMoreThan5).mapRight((lambda s: s + ' more than 5'), 'failed')
        assert s1.getLeft() == MB(3)
        assert s2.getLeft().get(42) == 3
        assert s4.getLeft(MB(42)) == MB(42)
        assert s4.getLeft(42) == MB(42)
        try:
            assert s4.getLeft(42).get().get() == 42
        except AttributeError:
            assert True
        else:
            assert False
        bar = 'barbell'
        bar = s1.getRight()
        assert bar == 'foofoo rules'
        assert s2.getRight() == 'more than 5'
        assert s3.getRight() == 'foofoo rules'
        assert s4.getRight() == 'foofoo rules more than 5'
        assert s1.getLeft(0) == MB(3)
        assert s3.getLeft(0) == MB(42)
        assert s4.getLeft(0) == MB(0)

    def test_either_bind(self) -> None:
        def lessThan2(x: int) -> XOR[int, str]:
            if x < 2:
                return XOR(x, 'fail!')
            else:
                return XOR(MB(), '>=2')

        def lessThan5(x: int) -> XOR[int, str]:
            if x < 5:
                return XOR(x, '')
            else:
                return XOR(MB(), '>=5')

        left1 = XOR(1, 'no')
        left4 = XOR(4, '')
        left7 = XOR(7, 'foobar')
        right: XOR[int, str] = XOR(MB(), 'Nobody home')

        nobody = right.bind(lessThan2)
        assert nobody == XOR(MB(), 'Nobody home')

        lt2 = left1.bind(lessThan2)
        lt5 = left1.bind(lessThan5)
        assert lt2 == XOR(1, 'foofoo rules')
        assert lt5 == XOR(1, '')

        lt2 = left4.bind(lessThan2)
        lt5 = left4.bind(lessThan5)
        assert lt2 == XOR(MB(), '>=2')
        assert lt5 == XOR(4, '>=5')

        lt2 = left7.bind(lessThan2)
        lt5 = left7.bind(lessThan5)
        assert lt2 == XOR(MB(), '>=2')
        assert lt5 == XOR(MB(), '>=5')

        nobody = right.bind(lessThan5)
        assert nobody == XOR(MB(), 'Nobody home')

        lt2 = left1.bind(lessThan2)
        lt5 = left1.bind(lessThan5)
        assert lt2 == XOR(1,'not me')
        assert lt5 == XOR(1, 'not me too')

        lt2 = left4.bind(lessThan2)
        lt5 = left4.bind(lessThan5)
        assert lt2 == XOR(MB(), '>=2')
        assert lt2 != XOR(42, '>=42')
        assert lt5 == XOR(4, 'boo')
        assert lt5 != XOR(42, 'boohoo')

        lt2 = left7.bind(lessThan2).mapRight(lambda _: 'greater than or equal 2',
                                                altRight='failed')
        lt5 = left7.bind(lessThan5).mapRight(lambda s: s + ', greater than or equal 5',
                                                altRight='failed')
        assert lt2 == XOR(MB(), 'greater than or equal 2')
        assert lt5 == XOR(MB(), '>=5, greater than or equal 5')

    def test_MB_XOR(self) -> None:
        mb42 = MB(42)
        mbNot: MB[int] = MB()

        left42 = XOR(mb42, 'failed')
        right = XOR[int, str](mbNot, 'Nobody home')
        assert left42 == XOR(42, 'fail!')
        assert right == XOR(MB(), 'Nobody home')

        ph42 = MB(XOR(left42, 'also a failure'))
        phNot1: MB[XOR[int, str]] = MB(XOR(MB(), ''))
        phNot2 = MB(XOR[int, str](MB(), ''))
        assert phNot1 == phNot2

    def test_XOR_No_Pot_Rt(self) -> None:
        dog1 = XOR('Lucy', 1)
        dog2 = XOR('Flash', 2)
        dog3 = XOR[str, int](MB(), 3)

        rt_dog1 = dog1.makeRight()
        rt_dog2 = dog2.newRight(42).makeRight()
        rt_dog3 = dog3.mapRight(lambda x: x+1, altRight=-1).makeRight()

