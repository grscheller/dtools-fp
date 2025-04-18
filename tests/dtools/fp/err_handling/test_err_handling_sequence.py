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

from typing import reveal_type
from dtools.tuples.ftuple import FTuple as FT
from dtools.tuples.ftuple import f_tuple as ft
from dtools.queues.restrictive import DoubleQueue as DQ, double_queue as dq
from dtools.fp.err_handling import MB, XOR

class TestMB_sequence:
    def test_no_empties(self) -> None:
        list_mb_int = list(map(MB, range(1, 2501)))
        tuple_mb_int = tuple(map(MB, range(1, 2501)))
#       ftuple_mb_int = ft(map(MB, range(1, 2501)))
        dqueue_mb_int = DQ(map(MB, range(1, 2501)))

        reveal_type(list_mb_int)
        reveal_type(tuple_mb_int)
#       reveal_type(ftuple_mb_int)
        reveal_type(dqueue_mb_int)

        mb_list_int = MB.sequence(list_mb_int).map(list)
        mb_tuple_int = MB.sequence(tuple_mb_int).map(tuple)
#       mb_ftuple_int = MB.sequence(ftuple_mb_int)
        mb_dqueue_int = MB.sequence(dqueue_mb_int).map(DQ)

        assert mb_list_int == MB(list(range(1, 2501)))
        assert mb_tuple_int == MB(tuple(range(1, 2501)))
#       assert mb_ftuple_int == MB(ft(range(1, 2501)))
        assert mb_dqueue_int == MB(DQ(range(1, 2501)))

    def test_with_empties(self) -> None:
        list_of_mb_int = [MB[int](), MB(2), MB(3), MB(4)]
        tuple_of_mb_int = MB(1), MB[int](), MB(3), MB(4)
        ftuple_of_mb_int = ft(MB(1), MB(2), MB[int](), MB(4))
        dqueue_of_mb_int = dq(MB(1), MB(2), MB(3), MB[int]())

        mb_list_int = MB.sequence(list_of_mb_int)
        mb_tuple_int = MB.sequence(tuple_of_mb_int)
        mb_ftuple_int = MB.sequence(ftuple_of_mb_int)
        mb_dqueue_int = MB.sequence(dqueue_of_mb_int)

        assert mb_list_int == MB()
        assert mb_tuple_int == MB()
        assert mb_ftuple_int == MB()
        assert mb_dqueue_int == MB()


class TestXOR_sequence:
    def test_no_rights(self) -> None:
        list_of_xor_int_str = list(map(lambda x: XOR(x, str(x)), range(1, 2501)))
        tuple_of_xor_int_str = tuple(map(lambda x: XOR(x, str(x)), range(1, 2501)))
#       ftuple_of_xor_int_str = FT(*map(lambda x: XOR(x, str(x)), range(1, 2501)))
        dqueue_of_xor_int_str = DQ(map(lambda x: XOR(x, str(x)), range(1, 2501)))

        xor_listInt_str = XOR.sequence(list_of_xor_int_str, 'OK').map(list)
        xor_tupleInt_str = XOR.sequence(tuple_of_xor_int_str, 'OK').map(tuple)
#       xor_ftuple_int_str: XOR[FT[int], str] = XOR.sequence(
#           ftuple_of_xor_int_str, 'OK'
#       )
        xor_dqueue_int_str: XOR[DQ[int], str] = XOR.sequence(
            dqueue_of_xor_int_str, 'OK'
        ).map(DQ)

        assert xor_listInt_str == XOR(list(range(1, 2501)), 'does not matter')
        assert xor_tupleInt_str == XOR(tuple(range(1, 2501)), 'for this test')
#       assert xor_ftuple_int_str == XOR(FT(*range(1, 2501)), 'all are lefts')
        assert xor_dqueue_int_str == XOR(DQ(range(1, 2501)), 'none are wrong')

    def test_with_rights(self) -> None:
        list_of_xor_int_str: list[XOR[int, str]] = [
            XOR(MB(), '1'),
            XOR(2, '2'),
            XOR(3, '3'),
            XOR(4, '4'),
        ]
        tuple_of_xor_int_str: tuple[XOR[int, str], ...] = (
            XOR(1, '1'),
            XOR(MB(), '2'),
            XOR(3, '3'),
            XOR(4, '4'),
        )
#       ftuple_of_xor_int_str = ft(
#           XOR(1, '1'), XOR(2, '2'), XOR(MB(), '3'), XOR(4, '4')
#       )
        dqueue_of_xor_int_str = dq(
            XOR(1, '1'), XOR(2, '2'), XOR(3, '3'), XOR(MB(), '4')
        )

        xor_list_int = XOR.sequence(list_of_xor_int_str, 'OK').map(list)
        xor_tuple_int = XOR.sequence(tuple_of_xor_int_str, 'OK').map(tuple)
#       xor_ftuple_int = XOR.sequence(ftuple_of_xor_int_str, 'OK').map(FT)
        xor_dqueue_int = XOR.sequence(dqueue_of_xor_int_str, 'OK').map(DQ)

        assert xor_list_int == XOR(MB(), '1')
        assert xor_tuple_int == XOR(MB(), '2')
#       assert xor_ftuple_int == XOR(MB(), '3')
        assert xor_dqueue_int == XOR(MB(), '4')
        assert xor_dqueue_int != XOR(MB(), '42')
