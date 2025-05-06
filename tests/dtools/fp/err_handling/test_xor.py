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

from typing import Never
from dtools.containers.tuples.ftuple import f_tuple as ft
from dtools.fp.err_handling import MayBe as MB
from dtools.fp.err_handling import Xor, LEFT, RIGHT


# -- Simple contrived tests ----------------------------------------------------


def gt42(x: int) -> bool | Never:
    """contrived function that fails for 42, returns a bool"""
    if x > 42:
        return True
    if x < 42:
        return False
    raise ValueError('x = 42')


def lt42(x: int) -> Xor[int, str] | Never:
    """contrived function that fails for 42, returns an Xor"""
    if x < 42:
        return Xor(x, LEFT)
    if x > 42:
        return Xor(f'{x}', RIGHT)
    raise ValueError('42 failed')


def lt42bool(x: int) -> Xor[bool, str] | Never:
    """contrived function that fails for 42, returns an Xor"""
    if x < 42:
        return Xor(True, LEFT)
    if x > 42:
        return Xor(f'{x}', RIGHT)
    raise ValueError('42 failed')


def fail_int(x: int) -> int | Never:
    """contrived function that fails for all but 1 unusual argument"""
    if x != -666:
        raise ValueError
    return x


def fail_str(s: str) -> str | Never:
    if s != '-666':
        raise ValueError
    return s


class TestSimole:
    """Simple tests"""

    def test_equal(self) -> None:
        """some non-systematic tests"""
        xor41 = Xor[int, str](40 + 1)
        xor42: Xor[int, str] = Xor(40 + 2)
        xor43: Xor[int, str] = Xor(40 + 3)
        xor_no42: Xor[int, str] = Xor('no 42', RIGHT)
        xor_fortytwo: Xor[str, int] = Xor('forty-two', LEFT)
        xor_str_42: Xor[str, int] = Xor(21 * 2, RIGHT)
        xor_42tuple: Xor[int, tuple[int, ...]] = Xor(42)
        xor42_tuple: Xor[int, tuple[int, ...]] = Xor((2, 3), side=RIGHT)

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

    def test_identity(self) -> None:
        """identity tests"""
        e1: Xor[int, str] = Xor(42)
        e2: Xor[int, str] = Xor(42)
        e3: Xor[int, str] = Xor('The secret is unknown', RIGHT)
        e4: Xor[int, str] = Xor('not 42', RIGHT)
        e5: Xor[int, str] = Xor('also not 42', RIGHT)
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
        """equality tests"""
        e1: Xor[int, str] = Xor(42, LEFT)
        e2: Xor[int, str] = Xor(42, LEFT)
        e3: Xor[int, str] = Xor('not 42', RIGHT)
        e4: Xor[int, str] = Xor('not 42', RIGHT)
        e5: Xor[int, str] = Xor('also not 42', RIGHT)
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

    def test_MB_Xor(self) -> None:
        """Proving a nothing can be stored in a something"""
        mb_42 = MB(42)
        mb_not: MB[int] = MB()

        left_mb_42: Xor[MB[int], str] = Xor(mb_42, LEFT)
        left_mb_not: Xor[MB[int], str] = Xor(mb_not, LEFT)
        assert left_mb_42 == Xor(MB(42), LEFT)
        assert left_mb_not == Xor(MB(), LEFT)

        phNot1: MB[Xor[MB[int], str]] = MB(Xor(MB[int](), LEFT))
        phNot2 = MB(Xor[int, str]('', RIGHT))
        assert phNot1 != phNot2

        none_to_the_left_1: Xor[None, None] = Xor(None, LEFT)
        none_to_the_left_2: Xor[None, None] = Xor(None, LEFT)
        none_to_the_right_1: Xor[None, None] = Xor(None, RIGHT)
        none_to_the_right_2: Xor[None, None] = Xor(None, RIGHT)

        assert none_to_the_left_1 == none_to_the_left_1
        assert none_to_the_left_2 == none_to_the_left_2
        assert none_to_the_left_1 == none_to_the_left_2
        assert none_to_the_right_1 == none_to_the_right_1
        assert none_to_the_right_2 == none_to_the_right_2
        assert none_to_the_right_1 == none_to_the_right_2
        assert none_to_the_left_1 != none_to_the_right_1
        assert none_to_the_left_2 != none_to_the_right_2


# -- Test map and map_right ----------------------------------------------------------


def add2ifLT5(x: int) -> int | Never:
    """Contrived function to fail if given 5"""
    if x < 5:
        return x + 2
    elif x > 5:
        return x
    else:
        raise ValueError


def add_1_if_gt_5(x: int) -> int:
    """Contrived function to fail if given 5"""
    if x == 5:
        raise ValueError
    if x > 5:
        return x + 1
    return x


def chk_str_starts_map(s: str) -> str | Never:
    """Contrived function to fail if str given does not start 'map'"""
    if s[0:3] == 'map':
        return f'{s}'
    else:
        raise ValueError


class TestMapAndNapRight:
    """Test map and map_right together"""

    def test_xor_map(self) -> None:
        """Test map by itself"""
        s2 = Xor[int, str](2, LEFT)
        s5 = Xor[int, str](5, LEFT)
        s10 = Xor[int, str](10, LEFT)
        s_foo_m = Xor[int, str]('foo', RIGHT)

        assert s2.get_left() == MB(2)
        assert s5.get_left() == MB(5)
        assert s10.get_left() == MB(10)
        assert s_foo_m.get_left() == MB()
        assert s2.get_right() == MB()
        assert s5.get_right() == MB()
        assert s10.get_right() == MB()
        assert s_foo_m.get_right() == MB('foo')

        s2 = s2.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s5 = s5.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s10 = s10.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s_foo_m = s_foo_m.map(add2ifLT5, 'map failed').map_right(
            (lambda s: 'The ' + s + '.'), 'The map.right failed!'
        )
        s_foo_cr = s_foo_m.change_right('Foofoo').map_right(
            (lambda s: s + ' rules!'), 'The map_right failed!'
        )

        assert s2.get_left() == MB(4)
        assert s5.get_left() == MB()
        assert s10.get_left() == MB(10)
        assert s_foo_m.get_left() == MB()
        assert s2.get_right() == MB()
        assert s5.get_right() == MB('The map failed.')
        assert s10.get_right() == MB()
        assert s_foo_m.get_right() == MB('The foo.')
        assert s_foo_cr.get_right() == MB('Foofoo rules!')

        try:
            s2g = s2.get()
            assert s2g == 4
            s10g = s10.get()
            assert s10g == 10
        except AssertionError:
            assert False
        except ValueError:
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

    def test_xor_maps(self) -> None:
        """Test map and map_right together"""

        s2 = Xor[int, str](2, LEFT)
        s5 = Xor[int, str](5, LEFT)
        s10 = Xor[int, str](10, LEFT)
        s_bar = Xor[int, str]('bar', RIGHT)

        s2g = s2.get()
        s10g = s10.get()
        s2gl = s2.get_left()
        s5gl = s5.get_left()
        s10gl = s10.get_left()
        s_bar_gl = s_bar.get_left()
        s2gr = s2.get_right()
        s5gr = s5.get_right()
        s10gr = s10.get_right()
        s_bar_gr = s_bar.get_right()

        assert s2g == 2
        assert s10g == 10
        assert s2gl == MB(2)
        assert s5gl == MB(5)
        assert s10gl == MB(10)
        assert s_bar_gl == MB()
        assert s2gr == MB()
        assert s5gr == MB()
        assert s10gr == MB()
        assert s_bar_gr == MB('bar')

        s2 = s2.map(add_1_if_gt_5, 'map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )
        s5 = s5.map(add_1_if_gt_5, 'the map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )
        s10 = s10.map(add_1_if_gt_5, 'my map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )
        s_bar = s_bar.map(add_1_if_gt_5, 'my map failed').map_right(
            chk_str_starts_map, 'The map_right failed!'
        )

        s2g = s2.get()
        s10g = s10.get()
        s2gl = s2.get_left()
        s5gl = s5.get_left()
        s10gl = s10.get_left()
        s_bar_gl = s_bar.get_left()
        s2gr = s2.get_right()
        s5gr = s5.get_right()
        s10gr = s10.get_right()
        s_bar_gr = s_bar.get_right()
        
        assert s2g == 2
        assert s10g == 11
        assert s2gl == MB(2)
        assert s5gl == MB()
        assert s10gl == MB(11)
        assert s_bar_gl == MB()
        assert s2gr == MB()
        assert s5gr == MB('The map_right failed!')
        assert s10gr == MB()
        assert s_bar_gr == MB('The map_right failed!')

        try:
            s2g = s2.get()
            s10g = s10.get()
            assert s2g == 2
            assert s10g == 11
        except AssertionError:
            assert False
        except ValueError:
            assert False

        try:
            s5g = s5.get()
            assert s5g > 0
        except AssertionError:
            assert False
        except ValueError:
            assert True

        try:
            s2g = s2.get()
            assert s2g != 2
        except AssertionError:
            assert True
        except ValueError:
            assert False

        try:
            s_bar_g = s_bar.get()
            assert s_bar_g != 2
        except AssertionError:
            assert False
        except ValueError:
            assert True


# -- Test map and map_right ----------------------------------------------------------


def lessThan2(x: int) -> Xor[int, str]:
    if x < 2:
        return Xor(x, LEFT)
    else:
        return Xor(f'{x} >= 2', RIGHT)


def lessThan5(x: int) -> Xor[int, str]:
    if x < 5:
        return Xor(x, LEFT)
    else:
        return Xor(f'{x} >= 5', RIGHT)


class TestBind:
    """Test map and map_right together"""

    def test_bind_simple(self) -> None:
        """Simple bind tests usinf an FTuple"""
        xor41 = Xor[int, str](41)
        xor42: Xor[int, str] = Xor(42)
        xor43: Xor[int, str] = Xor(43)

        ft_xor_int_str = ft(xor41, xor42, xor43)
        ft_xor_bool_str = ft_xor_int_str.map(lambda x: x.bind(lt42bool, 'bind failed'))

        assert ft_xor_bool_str[0] == Xor[bool, str](True, LEFT)
        assert ft_xor_bool_str[1] == Xor[bool, str]('bind failed', RIGHT)
        assert ft_xor_bool_str[2] == Xor[bool, str]('43', RIGHT)

    def test_xor_bind(self) -> None:
        left1 = Xor[int, str](1, LEFT)
        left4 = Xor[int, str](4, LEFT)
        left7 = Xor[int, str](7, LEFT)
        right: Xor[int, str] = Xor('Nobody home.', RIGHT)

        nobody = right.bind(lessThan2, 'Anybody home?')
        assert nobody == Xor('Nobody home.', RIGHT)

        lt2 = left1.bind(lessThan2, '')
        lt5 = left1.bind(lessThan5, '')
        assert lt2 == Xor(1, LEFT)
        assert lt5 == Xor(1, LEFT)

        lt2 = left4.bind(lessThan2, '')
        lt5 = left4.bind(lessThan5, '')
        assert lt2 == Xor('4 >= 2', RIGHT)
        assert lt5 == Xor(4)

        lt2 = left7.bind(lessThan2, '')
        lt5 = left7.bind(lessThan5, '')
        assert lt2 == Xor('7 >= 2', RIGHT)
        assert lt5 == Xor('7 >= 5', RIGHT)

        nobody = right.bind(lessThan5, '')
        assert nobody == Xor('Nobody home.', RIGHT)

        lt2 = left1.bind(lessThan2, '')
        lt5 = left1.bind(lessThan5, '')
        assert lt2 == Xor(1, LEFT)
        assert lt5 == Xor(1, LEFT)

        lt2 = left4.bind(lessThan2, '')
        lt5 = left4.bind(lessThan5, '')
        assert lt2 == Xor('4 >= 2', RIGHT)
        assert lt2 != Xor('42 >= 2', RIGHT)
        assert lt5 == Xor(4, LEFT)
        assert lt5 != Xor('5 >= 5', RIGHT)

        lt2 = left7.bind(lessThan2, 'bind failed').map_right(
            lambda _: 'greater than or equal 2', alt_right='map_right failed'
        )
        lt5 = left7.bind(lessThan5, 'bind failed').map_right(
            lambda s: s + ', greater than or equal 5', 'map_right failed'
        )
        assert lt2 == Xor('greater than or equal 2', RIGHT)
        assert lt5 == Xor('7 >= 5, greater than or equal 5', RIGHT)


class TestXorUsecases:
    """Non-systematic tests for ease of use"""

    def test_usecase(self) -> None:
        ""
        xor_99 = Xor[int, str](99, LEFT)
        xor_86 = Xor[int, str]('Max', RIGHT)
        xor_49 = Xor[int, str](49, LEFT)
        xor_42 = Xor[int, str](42, LEFT)
        xor_21 = Xor[int, str](21, LEFT)
        xor_12 = Xor[int, str](12, LEFT)
        xor_01 = Xor[int, str](1, LEFT)

        assert xor_99.get() == 99
        assert xor_99.get_right() == MB()
        try:
            agent = xor_86.get()
            assert agent == 86
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False
        assert xor_86.get_right() == MB('Max')

        kaos0: Xor[bool, str] = Xor(True, LEFT)
        kaos1 = xor_99.map(gt42, 'left 99')
        kaos2 = xor_49.map(gt42, 'left 49')
        assert kaos0 == kaos1 == kaos2

        kaos0 = Xor(False, LEFT)
        kaos1 = xor_01.map(gt42, 'failed')
        kaos2 = xor_86.map(gt42, 'failed')
        kaos3: Xor[bool, str] = Xor('Max', RIGHT)
        assert kaos0 == kaos1 != kaos2 == kaos3

        kaos0 = Xor(False, LEFT)
        kaos1 = xor_12.map(gt42, 'failed')
        kaos2 = xor_21.map(gt42, 'failed')
        assert kaos0 == kaos1 == kaos2

        kaos0 = Xor('map failed', RIGHT)
        kaos1 = xor_42.map(gt42, 'map failed')
        assert kaos0 == kaos1

        chief1 = xor_86.map_right(
            (lambda s: f'{s}, you idiot!'), 'Not the dome of silence!'
        )
        chief2 = xor_42.map(gt42, 'Smart').map_right(
            (lambda s: f"{s}, you're fired!"), 'Not the dome of silence!'
        )
        chief3 = xor_86.map_right(fail_str, 'Not the dome of silence!')
        chief4 = xor_99.map_right(fail_str, 'Not the dome of silence!')
        hymie99 = xor_99.map((lambda s: f'Hello agent {s}!'), 'Got some oil?')
        hymie21 = xor_21.bind(lt42, 'Seigfried').map(
            (lambda s: f'Hello agent {s}!'), 'Got some oil?'
        )
        hymie42 = xor_42.bind(lt42, 'Ratton').map_right(fail_str, 'Got some oil?')

        assert chief1 != chief2
        assert chief3 != chief4
        assert chief1 == Xor('Max, you idiot!', RIGHT)
        assert chief2 == Xor("Smart, you're fired!", RIGHT)
        assert chief3 == Xor('Not the dome of silence!', RIGHT)
        assert chief4 == Xor(99, LEFT)
        assert hymie99 == Xor('Hello agent 99!', LEFT)
        assert hymie21 == Xor('Hello agent 21!', LEFT)
        assert hymie42 == Xor('Got some oil?', RIGHT)
