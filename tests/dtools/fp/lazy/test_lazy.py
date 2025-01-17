# Copyright 2024-2025 Geoffrey R. Scheller
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

from typing import Any, Final, Never
from dtools.fp.err_handling import MB, XOR
from dtools.fp.lazy import Lazy, lazy

def add2_if_pos(x: int) -> int:
    if x < 1:
        raise ValueError
    return x + 2

def evaluate_it(lz: Lazy[int, int]) -> int:
    if lz.eval():
        return lz.result().get()
    else:
        return -1

class Test_Lazy:
    def test_happy_path(self) -> None:
        assert evaluate_it(Lazy(add2_if_pos, 5)) == 7

    def test_sad_path(self) -> None:
        assert evaluate_it(Lazy(add2_if_pos, -42)) == -1

#---------------------------------------------------------------

def hello() -> str:
    hello = "helloooo"
    while len(hello) > 1:
        if hello == 'hello':
            return hello
        else:
            hello = hello[:-1]
    raise ValueError('hello')

def no_hello() -> str:
    hello = "helloooo"
    while len(hello) > 1:
        if hello == 'hello':
            raise ValueError('failed as expected')
        else:
            hello = hello[:-1]
    return hello

def return_str(lz: Lazy[Any, str]) -> str:
    if lz.eval():
        return lz.result().get()
    else:
        esc = lz.exception().get()
        return f'Error: {esc}'

class Test_Lazy_0_1:
    def test_happy_path(self) -> None:
        lz_good = lazy(hello, pure=False)
        assert return_str(lz_good) == 'hello'

    def test_sad_path(self) -> None:
        lz_bad = lazy(no_hello, pure=False)
        assert return_str(lz_bad) == 'Error: failed as expected'

#---------------------------------------------------------------

class counter():
    def __init__(self, n: int=0) -> None:
        self._cnt = n

    def inc(self) -> None:
        self._cnt += 1

    def get(self) -> int:
        return self._cnt

    def set(self, n: int) -> None:
        self._cnt = n

class Test_Lazy_0_0:
    def test_pure(self) -> None:
        cnt1 = counter(0)

        lz_p = lazy(cnt1.inc, pure=True)
        lz_n = lazy(cnt1.inc, pure=False)

        if lz_p:
            assert False
        if lz_p.is_evaluated():
            assert False
        if lz_p.is_exceptional():
            assert False
        if lz_n:
            assert False
        if lz_n.is_evaluated():
            assert False
        if lz_n.is_exceptional():
            assert False
        assert cnt1.get() == 0
        assert lz_n.eval() == True
        assert cnt1.get() == 1
        if lz_p:
            assert False
        if lz_p.is_evaluated():
            assert False
        if lz_p.is_exceptional():
            assert False
        if lz_n:
            assert True
        if lz_n.is_evaluated():
            assert True
        if lz_n.is_exceptional():
            assert False
        assert lz_p.eval() == True
        assert cnt1.get() == 2
        if lz_p:
            assert True
        if lz_p.is_evaluated():
            assert True
        if lz_p.is_exceptional():
            assert False
        assert lz_p.eval() == True
        assert cnt1.get() == 2
        assert lz_n.eval() == True
        assert cnt1.get() == 3
        assert lz_p.eval() == True
        assert cnt1.get() == 3
        assert lz_n.eval() == True
        assert cnt1.get() == 4
        assert lz_n.eval() == True
        assert cnt1.get() == 5
        assert lz_p.eval() == True
        assert cnt1.get() == 5

class Test_Lazy_1_0:
    def test_pure(self) -> None:
        cnt2 = counter(0)

        lz_p = Lazy(cnt2.set, 2, pure=True)
        lz_n = Lazy(cnt2.set, 5, pure=False)

        if lz_p:
            assert False
        if lz_p.is_evaluated():
            assert False
        if lz_p.is_exceptional():
            assert False
        if lz_n:
            assert False
        if lz_n.is_evaluated():
            assert False
        if lz_n.is_exceptional():
            assert False
        assert lz_p.eval() == True
        assert cnt2.get() == 2
        assert lz_n.eval() == True
        assert cnt2.get() == 5
        assert lz_p.eval() == True
        assert cnt2.get() == 5
        cnt2.inc()
        assert cnt2.get() == 6
        assert lz_p.eval() == True
        assert cnt2.get() == 6
        assert lz_n.eval() == True
        assert cnt2.get() == 5

#---------------------------------------------------------------

class Test_lazy:
    def test_lazy_0(self) -> None:
        def foo42() -> int:
            return 42

        def bar42() -> int:
            raise RuntimeError('not 42')

        class FooBar():
            def __init__(self, secret: int):
                self._secret = secret

            def get_secret(self) -> int:
                if (ret := self._secret) != 13:
                    return ret
                else:
                    raise RuntimeError(13)

        lz_42 = lazy(foo42)
        if lz_42.eval():
            assert lz_42.result().get(-1) == 42
            assert lz_42.exception() == MB()
        else:
            assert False

        lz_not_42 = lazy(bar42)
        if lz_not_42.eval():
            assert False
        else:
            assert lz_not_42.result().get(-1) == -1
            assert str(lz_not_42.exception().get()) == 'not 42'

        fb7 = FooBar(7)
        lz_fb7 = lazy(fb7.get_secret)
        if lz_fb7.eval():
            assert lz_fb7.result().get(-1) == 7
            assert lz_fb7.exception() == MB()
        else:
            assert False

        fb13 = FooBar(13)
        lz_fb13 = lazy(fb13.get_secret)
        if lz_fb13.eval():
            assert False
        else:
            assert lz_fb13.result().get(-1) == -1
            assert str(lz_fb13.exception().get()) == '13'

