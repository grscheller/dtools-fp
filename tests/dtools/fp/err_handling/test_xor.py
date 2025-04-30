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

from typing import Any, Never
from dtools.tuples.ftuple import f_tuple as ft
from dtools.fp.err_handling import MB, XOR, LEFT, RIGHT


def gt42(x: int) -> bool|Never:
    """function that fails for 42, returns a bool"""
    if x > 42:
        return True
    if x < 42:
        return False
    raise ValueError('x = 42')

def lt42(x: int) -> XOR[int, str]|Never:
    """function that fails for 42, returns an XOR"""
    if x < 42:
        return XOR(x, LEFT)
    if x > 42:
        return XOR(f'{x}', RIGHT)
    raise ValueError(f'{42}')

def fail(x: Any) -> Never:
    raise AttributeError

class TestXOR:
    def test_usecase(self) -> None:
        """Non-systematic tests for ease of use"""
        xor_99 = XOR[int, str](99, LEFT)
        xor_86 = XOR[int, str]('Max', RIGHT)
        xor_49 = XOR[int, str](49)
        xor_42 = XOR[int, str](42)
        xor_42_clone = XOR[int, str](42)
        xor_21 = XOR[int, str](21)
        xor_12 = XOR[int, str](12)
        xor_03 = XOR[int, str]('Max', RIGHT)
        xor_02 = XOR[int, str]('2', RIGHT)
        xor_01 = XOR[int, str](1)

        assert xor_99.get() == 99
        assert xor_99.get_right() == MB()
        try:
            assert xor_86.get() == 86
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False
        assert xor_86.get_right() == MB('Max')

        assert            XOR(True, LEFT) == xor_99.map(gt42, 'left 99')            == xor_49.map(gt42, 'left 49')
        assert           XOR(False, LEFT) == xor_01.map(gt42, 'map failed')         != xor_86.map(gt42, 'map failed') == XOR('Max', RIGHT)
        assert           XOR(False, LEFT) == xor_12.map(gt42, 'map failed')         == xor_21.map(gt42, 'map failed')
        assert       XOR('failed', RIGHT) == xor_42.map(gt42, 'failed')             == xor_42_clone.map(gt42, 'failed')
        assert XOR('clone failed', RIGHT) == xor_42_clone.map(gt42, 'clone failed') != xor_42.map(gt42, 'failed')     == XOR('failed', RIGHT)

        chief1 = xor_86.map_right(
            (lambda s: f'{s}, you idiot!'), 'Not the dome of silence!'
        )
        chief2 = xor_42.map(gt42, 'Smart').map_right(
            (lambda s: f'{s}, you idiot!'), 'Not the dome of silence!'
        )
        chief3 = xor_86.map_right(fail, 'Not the dome of silence!')
        chief4 = xor_99.map_right(fail, 'Not the dome of silence!')
        hymie99 = xor_99.map(
            (lambda s: f'Hymie says: Hello agent {s}!'), 'Got some oil?'
        )
        hymie21 = xor_21.bind(lt42, 'Seigfried').map(
            (lambda s: f'Hymie says: Hello agent {s}!'), 'Got some oil?'
        )
        hymie42 = xor_42.bind(lt42, 'Ratton').map_right(fail, 'Got some oil?')

        assert chief1 != chief2
        assert chief3 != chief4
        assert chief1 == XOR('Max, you idiot!', RIGHT)
        assert chief2 == XOR('Smart, you idiot!', RIGHT)
        assert chief3 == XOR('Not the dome of silence!', RIGHT)
        assert chief4 == XOR(True, LEFT)
        assert hymie99 == XOR('Hello agent 99!', LEFT)
        assert hymie21 == XOR('Hello agent 21!', LEFT)
        assert hymie42 == XOR('Got some oil?', RIGHT)

    def test_equal(self) -> None:
        """some non-systematic tests"""
        xor41 = XOR[int, str](40 + 1)
        xor42: XOR[int, str] = XOR(40 + 2)
        xor43: XOR[int, str] = XOR(40 + 3)
        xor_no42: XOR[int, str] = XOR('no 42', RIGHT)
        xor_fortytwo: XOR[str, int] = XOR('forty-two', LEFT)
        xor_str_42: XOR[str, int] = XOR(21 * 2, RIGHT)
        xor_42tuple: XOR[int, tuple[int, ...]] = XOR(42)
        xor42_tuple: XOR[int, tuple[int, ...]] = XOR((2, 3), side=RIGHT)

        assert xor42 == xor42
        assert xor_no42 == xor_no42
        assert xor_fortytwo == xor_fortytwo
        assert xor_str_42 == xor_str_42
        assert xor_42tuple == xor_42tuple
        assert xor42_tuple == xor42_tuple

        assert xor41 != xor43
        assert xor42 != xor_fortytwo
        assert xor42 != xor_str_42
        assert xor42 == xor_42tuple
        assert xor_42tuple != xor42_tuple

        ft_xor_int_str = ft(xor41, xor42, xor43)
        ft_xor_bool_str = ft_xor_int_str.map(lambda x: x.bind(lt42, 'failure'))

        assert ft_xor_bool_str[0] == XOR[bool, str](True, LEFT)
        assert ft_xor_bool_str[1] == XOR[bool, str](False, LEFT)
        assert ft_xor_bool_str[2] == XOR[bool, str]('43', RIGHT)

    def test_identity(self) -> None:
        e1: XOR[int, str] = XOR(42)
        e2: XOR[int, str] = XOR(42)
        e3: XOR[int, str] = XOR('The secret is unknown', RIGHT)
        e4: XOR[int, str] = XOR('not 42', RIGHT)
        e5: XOR[int, str] = XOR('also not 42', RIGHT)
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
        e1: XOR[int, str] = XOR(42, LEFT)
        e2: XOR[int, str] = XOR(42, LEFT)
        e3: XOR[int, str] = XOR('not 42', RIGHT)
        e4: XOR[int, str] = XOR('not 42', RIGHT)
        e5: XOR[int, str] = XOR('also not 42', RIGHT)
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

    def test_xor_map(self) -> None:
        def add2ifLT5(x: int) -> int | Never:
            """Contrived function to fail if given 5"""
            if x < 5:
                return x + 2
            elif x > 5:
                return x
            else:
                raise ValueError

        s2 = XOR[int, str](2)
        s5 = XOR[int, str](5)
        s10 = XOR[int, str](10)
        s2 = s2.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s5 = s5.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s10 = s10.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )

        assert s2.get(42) == 4
        assert s5.get(42) == 42
        assert s10.get(42) == 10
        assert s2.get(MB(42)) == 4
        assert s5.get(MB(42)) == 42
        assert s10.get(MB(42)) == 10
        assert s2.get_right() == MB()
        assert s5.get_right() == MB('The map failed.')
        assert s10.get_right() == MB()

        try:
            assert s2.get() == 4
            assert s10.get() == 10
        except AssertionError:
            assert False
        else:
            assert True

        try:
            assert s5.get() > 0
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False

        try:
            assert s2.get() == 2
        except AssertionError:
            assert True
        except ValueError:
            assert False
        else:
            assert False

    def test_xor_map_right(self) -> None:
        def add_1_if_gt_5(x: int) -> int:
            """Contrived function to fail if given 5"""
            if x == 5:
                raise ValueError
            if x > 5:
                return x + 1
            return x

        def chk_str_starts_map(s: str) -> str|Never:
            """Contrived function to fail if str given does not start 'map'"""
            if s[0:3] == 'map':
                return 's'
            else:
                raise ValueError

        s2 = XOR[int, str](2)
        s5 = XOR[int, str](5)
        s10 = XOR[int, str](10)
        s2 = s2.map(add_1_if_gt_5, 'map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )
        s5 = s5.map(add_1_if_gt_5, 'the map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )
        s10 = s10.map(add_1_if_gt_5, 'my map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )

        assert s2.get(42) == 2
        assert s5.get(42) == 42
        assert s10.get(42) == 11
        assert s2.get(MB(42)) == 2
        assert s5.get(MB(42)) == 42
        assert s10.get(MB(42)) == 11
        assert s2.get_right() == MB()
        assert s5.get_right() == MB('The map_right failed!')
        assert s10.get_right() == MB()

        try:
            assert s2.get() == 2
            assert s10.get() == 11
        except AssertionError:
            assert False
        else:
            assert True

        try:
            assert int(s5.get()) > 0
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False

        try:
            assert s2.get() != 2
        except AssertionError:
            assert True
        except ValueError:
            assert False
        else:
            assert False

    def test_xor_bind(self) -> None:
        def lessThan2(x: int) -> XOR[int, str]:
            if x < 2:
                return XOR(x, LEFT)
            else:
                return XOR(f'{x} >= 2', RIGHT)

        def lessThan5(x: int) -> XOR[int, str]:
            if x < 5:
                return XOR(x, LEFT)
            else:
                return XOR('x >= 5', RIGHT)

        left1 = XOR[int, str](1, LEFT)
        left4 = XOR[int, str](4, LEFT)
        left7 = XOR[int, str](7, LEFT)
        right: XOR[int, str] = XOR('Nobody home', RIGHT)

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
        assert lt2 == XOR(1, 'not me')
        assert lt5 == XOR(1, 'not me too')

        lt2 = left4.bind(lessThan2)
        lt5 = left4.bind(lessThan5)
        assert lt2 == XOR(MB(), '>=2')
        assert lt2 != XOR(42, '>=42')
        assert lt5 == XOR(4, 'boo')
        assert lt5 != XOR(42, 'boohoo')

        lt2 = left7.bind(lessThan2).map_right(
            lambda _: 'greater than or equal 2', alt_right='failed'
        )
        lt5 = left7.bind(lessThan5).map_right(
            lambda s: s + ', greater than or equal 5', alt_right='failed'
        )
        assert lt2 == XOR(MB(), 'greater than or equal 2')
        assert lt5 == XOR(MB(), '>=5, greater than or equal 5')

    def test_MB_XOR(self) -> None:
        mb42 = MB(42)
        mbNot: MB[int] = MB()

        left42 = XOR(mb42, 'failed')
        right = XOR[int, str](mbNot, 'Nobody home')
        assert left42 == XOR(42, 'fail!')
        assert right == XOR(MB(), 'Nobody home')

        phNot1: MB[XOR[int, str]] = MB(XOR(MB(), ''))
        phNot2 = MB(XOR[int, str](MB(), ''))
        assert phNot1 == phNot2
