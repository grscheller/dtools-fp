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
from dtools.fp.singletons import NoValue
from dtools.fp.err_handling import MayBe as MB
from dtools.fp.err_handling import Xor, LEFT, RIGHT

_noValue: Final[NoValue] = NoValue()

def add_lt_42(x: int, y: int) -> MB[int]:
    sum_xy = x + y
    if sum_xy < 42:
        return MB(sum_xy)
    else:
        return MB()

def add_gt_42(x: int, y: int) -> Xor[int, str]:
    sum_xy = x + y
    if sum_xy > 42:
        return Xor(sum_xy)
    else:
        return Xor('too small', RIGHT)

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

    def test_Xor_str(self) -> None:
        assert str(Xor[int, str](10)) == '< 10 | >'
        assert str(add_gt_42(10, -4)) == '< | too small >'
        assert str(add_gt_42(10, 40)) == "< 50 | >"
        assert str(Xor('Foofoo rules', RIGHT)) == "< | Foofoo rules >"
        assert str(Xor[int, str](42)) == "< 42 | >"
        assert str(Xor[str, int]('foofoo')) == "< foofoo | >"

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

        mb_str = MB('foo')
        mb_str_2 = eval(repr(mb_str))
        assert mb_str_2 == mb_str
        assert repr(mb_str_2) == repr(mb_str) =="MB('foo')"
        if mb_str:
            assert True
        else:
            assert False

        mb_str0 = MB('')
        mb_str0_2 = eval(repr(mb_str0))
        assert mb_str0_2 == mb_str0
        assert repr(mb_str0_2) == repr(mb_str0) =="MB('')"
        if mb_str0:
            assert True
        else:
            assert False

        mb_none = MB(None)
        mb_none_2 = eval(repr(mb_none))
        assert mb_none_2 == mb_none
        assert repr(mb_none_2) == repr(mb_none_2) =="MB(None)"
        if mb_none:
            assert True
        else:
            assert False

        mb_never: MB[str] = MB()
        mb_never_2 = eval(repr(mb_never))
        assert mb_never_2 == mb_never
        assert repr(mb_never_2) == repr(mb_never) =="MB()"
        if mb_never:
            assert False
        else:
            assert True

        mbmb_str = MB(MB('foo'))
        mbmb_str_2 = eval(repr(mbmb_str))
        assert mbmb_str_2 == mbmb_str
        assert repr(mbmb_str_2) == repr(mbmb_str) =="MB(MB('foo'))"
        if mbmb_str:
            assert True
        else:
            assert False

        mbmb_str0 = MB(MB(''))
        mbmb_str0_2 = eval(repr(mbmb_str0))
        assert mbmb_str0_2 == mbmb_str0
        assert repr(mbmb_str0_2) == repr(mbmb_str0) =="MB(MB(''))"
        if mbmb_str0:
            assert True
        else:
            assert False

        mbmb_none = MB(MB(None))
        mbmb_none_2 = eval(repr(mbmb_none))
        assert mbmb_none_2 == mbmb_none
        assert repr(mbmb_none_2) == repr(mbmb_none_2) =="MB(MB(None))"
        if mbmb_none:
            assert True
        else:
            assert False

        mbmb_never: MB[MB[str]] = MB(MB())
        mbmb_never_2 = eval(repr(mbmb_never))
        assert mbmb_never_2 == mbmb_never
        assert repr(mbmb_never_2) == repr(mbmb_never) =="MB(MB())"
        if mbmb_never:
            assert True
        else:
            assert False

    def test_xor_repr(self) -> None:
        e1: Xor[int, str] = Xor('Nobody home!', RIGHT)
        e2: Xor[int, str] = Xor('Somebody not home!', RIGHT)
        e3: Xor[int, str] = Xor(5, LEFT)
        assert e1 != e2
        e5 = eval(repr(e2))
        assert e2 != Xor('Nobody home!', RIGHT)
        assert e2 == Xor('Somebody not home!', RIGHT)
        assert e5 == e2
        assert e5 != e3
        assert e5 is not e2
        assert e5 is not e3

        def lt5_or_nothing(x: int) -> MB[int]:
            if x < 5:
                return MB(x)
            else:
                return MB()

        def lt5_or_str(x: int) -> Xor[int, str]:
            if x < 5:
                return Xor(x)
            else:
                return Xor(f'was to be {x}', RIGHT)

        e6 = lt5_or_nothing(2)
        e7 = lt5_or_str(2)
        e8 = lt5_or_str(3)
        e9 = lt5_or_nothing(7)
        e10 = Xor[int, str](10).bind(lt5_or_str, 'bind_failed')

        assert e6 != e7
        assert e7 != e8
        assert e9 != e10
        assert e8 == eval(repr(e7)).map(lambda x: x+1, 'Who is John Gult?')

        assert repr(e6) ==  "MB(2)"
        assert repr(e7) ==  "Xor(2, LEFT)"
        assert repr(e8) ==  "Xor(3, LEFT)"
        assert repr(e9) == "MB()"
        assert repr(e10) ==  "Xor('was to be 10', RIGHT)"
