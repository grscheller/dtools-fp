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

from typing import Final
from dtools.fp.bool import _False
from dtools.fp.singletons import NoValue
from dtools.fp.err_handling import MB, XOR

_noValue: Final[NoValue] = NoValue()
False_: Final[_False] = _False()

def add_lt_42(x: int, y: int) -> MB[int]:
    sum_xy = x + y
    if sum_xy < 42:
        return MB(sum_xy)
    else:
        return MB()

def add_gt_42(x: int, y: int) -> XOR[int, str]:
    sum_xy = x + y
    if sum_xy > 42:
        return XOR(sum_xy)
    else:
        return XOR('too small', False_)

class Test_str:
    def test_MB_str(self) -> None:
        n1: MB[int] = MB()
        o1 = MB(42)
        assert str(n1) == 'MB()'
        assert str(o1) == 'MB(42)'
        mb1 = add_lt_42(3, 7)
        mb2 = add_lt_42(15, 30)
        assert str(mb1) == 'MB(10)'
        assert str(mb2) == 'MB()'
        nt1: MB[int] = MB()
        assert str(nt1) == str(mb2) =='MB()'

    def test_XOR_str(self) -> None:
        assert str(XOR[int, str](10)) == '< 10 | >'
        assert str(add_gt_42(10, -4)) == '< | too small >'
        assert str(add_gt_42(10, 40)) == "< 50 | >"
        assert str(XOR('Foofoo rules', False_)) == "< | Foofoo rules >"
        assert str(XOR[int, str](42)) == "< 42 | >"
        assert str(XOR[str, int]('foofoo')) == "< foofoo | >"

    def test_noValue_str(self) -> None:
        assert str(_noValue) == 'NoValue()'

class Test_repr:
    def test_mb_repr(self) -> None:
        mb1: MB[object] = MB()
        mb2: MB[object] = MB()
        mb3: MB[object] = MB(NoValue())
        mb4: MB[object] = MB(42)
        assert mb1 == mb2 == MB()
        assert mb3 == MB(NoValue()) != MB()
        assert repr(mb2) == 'MB()'
        mb5 = eval(repr(mb3))
        mb6 = eval(repr(mb4))
        assert mb5 == mb3
        assert mb6 == mb4

        def lt5orNothing(x: int) -> MB[int]:
            if x < 5:
                return MB(x)
            else:
                return MB()

        mb7 = lt5orNothing(3)
        mb8 = lt5orNothing(9)
        mb9 = lt5orNothing(18)

        assert mb6 != mb7
        assert mb8 == mb9

        assert repr(mb5) == repr(mb3) ==  'MB(NoValue())'
        assert repr(mb7) ==  'MB(3)'
        assert repr(mb8) == repr(mb9) ==  'MB()'

        foofoo = MB(MB('foo'))
        foofoo2 = eval(repr(foofoo))
        assert foofoo2 == foofoo
        assert repr(foofoo2) == repr(foofoo) =="MB('foo')"
        if foofoo:
            assert True
        else:
            assert False

    def test_xor_repr(self) -> None:
        e1: XOR[int, str] = XOR('Nobody home!', False_)
        e2: XOR[int, str] = XOR('Somebody not home!', False_)
        e3: XOR[int, str] = XOR(5)
        assert e1 != e2
        e5 = eval(repr(e2))
        assert e2 != XOR('Nobody home!', False_)
        assert e2 == XOR('Somebody not home!', False_)
        assert e5 == e2
        assert e5 != e3
        assert e5 is not e2
        assert e5 is not e3

        def lt5_or_nothing(x: int) -> MB[int]:
            if x < 5:
                return MB(x)
            else:
                return MB()

        def lt5_or_str(x: int) -> XOR[int, str]:
            if x < 5:
                return XOR(x)
            else:
                return XOR(f'was to be {x}', False_)

        e6 = lt5_or_nothing(2)
        e7 = lt5_or_str(2)
        e8 = lt5_or_str(3)
        e9 = lt5_or_nothing(7)
        e10 = XOR[int, str](10).bind(lt5_or_str)

        assert e6 != e7
        assert e7 != e8
        assert e9 != e10
        assert e8 == eval(repr(e7)).map(lambda x: x+1, 'Who is John Gult?')

        assert repr(e6) ==  "MB(2)"
        assert repr(e7) ==  "XOR(2)"
        assert repr(e8) ==  "XOR(3)"
        assert repr(e9) == "MB()"
        assert repr(e10) ==  "XOR('was to be 10', _False())"
