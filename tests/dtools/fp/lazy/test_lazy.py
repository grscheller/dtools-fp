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

from typing import Any, Iterator
from dtools.fp.err_handling import MB
from dtools.fp.lazy import Lazy, lazy, real_lazy

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
        lz_good = lazy(hello)
        assert return_str(lz_good) == 'hello'

    def test_sad_path(self) -> None:
        lz_bad = lazy(no_hello)
        assert return_str(lz_bad) == 'Error: failed as expected'

#---------------------------------------------------------------

class Counter():
    def __init__(self, n: int=0) -> None:
        self._cnt = n

    def inc(self) -> None:
        self._cnt += 1

    def get(self) -> int:
        return self._cnt

    def set(self, n: int) -> None:
        self._cnt = n

class TestLazy00:
    def test_pure(self) -> None:
        cnt1 = Counter(0)

        lz_p = real_lazy(cnt1.inc)
        lz_n = lazy(cnt1.inc)

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
        assert lz_n.eval()
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
        assert lz_p.eval()
        assert cnt1.get() == 2
        if lz_p:
            assert True
        if lz_p.is_evaluated():
            assert True
        if lz_p.is_exceptional():
            assert False
        assert lz_p.eval() is True
        assert cnt1.get() == 2
        assert lz_n.eval()
        assert cnt1.get() == 3
        assert lz_p.eval()
        assert cnt1.get() == 3
        assert lz_n.eval()
        assert cnt1.get() == 4
        assert lz_n.eval()
        assert cnt1.get() == 5
        assert lz_p.eval()
        assert cnt1.get() == 5

class TestLazy10:
    def test_pure(self) -> None:
        cnt2 = Counter(0)

        lz_p = real_lazy(cnt2.set, 2)
        lz_n = lazy(cnt2.set, 5)

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
        assert lz_p.eval() is True
        assert cnt2.get() == 2
        assert lz_n.eval()
        assert cnt2.get() == 5
        assert lz_p.eval()
        assert cnt2.get() == 5
        cnt2.inc()
        assert cnt2.get() == 6
        assert lz_p.eval()
        assert cnt2.get() == 6
        assert lz_n.eval()
        assert cnt2.get() == 5

#---------------------------------------------------------------

class TestLazy:
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

        lz_42 = real_lazy(foo42)
        if lz_42.eval():
            assert lz_42.result().get(-1) == 42
            assert lz_42.exception() == MB()
        else:
            assert False

        lz_not_42 = real_lazy(bar42)
        if lz_not_42.eval():
            assert False
        else:
            assert lz_not_42.result().get(-1) == -1
            assert str(lz_not_42.exception().get()) == 'not 42'

        fb7 = FooBar(7)
        lz_fb7 = real_lazy(fb7.get_secret)
        if lz_fb7.eval():
            assert lz_fb7.result().get(-1) == 7
            assert lz_fb7.exception() == MB()
        else:
            assert False

        fb13 = FooBar(13)
        lz_fb13 = real_lazy(fb13.get_secret)
        if lz_fb13.eval():
            assert False
        else:
            assert lz_fb13.result().get(-1) == -1
            assert str(lz_fb13.exception().get()) == '13'

    def test_lazy_mixed_and_shared_state(self) -> None:
        it5 = iter((6,5,4,3,2,1))

        def foo(name: str, it: Iterator[int]) -> str:
            try:
                ii = next(it)
            except StopIteration:
                ii = 0
            return name*ii

        lz_foo = lazy(foo, 'foo', it5)
        assert next(it5) == 6
        assert not lz_foo.is_evaluated()
        assert lz_foo.eval()
        assert lz_foo.is_evaluated()
        assert lz_foo.result().get('boobooboobooboo') == 'foofoofoofoofoo'
        assert lz_foo.is_evaluated()
        assert next(it5) == 4
        assert lz_foo.eval()
        assert lz_foo.exception() == MB()
        assert lz_foo.result() == MB('foofoofoo')

        lz_foo_pure = real_lazy(foo, 'foo', it5)
        if lz_foo_pure.eval():
            assert lz_foo_pure.result().get() == 'foofoo'
        else:
            assert False

        if lz_foo_pure.eval():
            assert lz_foo_pure.result().get() == 'foofoo'
        else:
            assert False

        if lz_foo.eval():
            assert lz_foo.result().get() == 'foo'
        else:
            assert False

        if lz_foo.eval():
            assert lz_foo.result().get() == ''
        else:
            assert False

        if lz_foo.eval():
            assert lz_foo.result().get() == ''
        else:
            assert False

    def test_lazy_failures(self) -> None:

        lz_add2_42 = real_lazy(add2_if_pos, 40)
        lz_add2_2 = real_lazy(add2_if_pos, 0)

        if lz_add2_42.eval():
            assert lz_add2_42.result() == MB(42)
        else:
            assert False

        if lz_add2_2.eval():
            assert False
        else:
            mb_exception = lz_add2_2.exception()
            if mb_exception:
                assert isinstance(mb_exception.get(), ValueError)

