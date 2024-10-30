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

from grscheller.datastructures.tuples import FTuple, FT
from grscheller.datastructures.queues import DoubleQueue, DQ
from grscheller.fp.err_handling import MB, XOR, sequence_mb, sequence_xor

class TestMB_sequence:
    def test_no_empties(self) -> None:
        list_of_mb_int = list(map(lambda x: MB(x), range(1, 2501)))
        tuple_of_mb_int = tuple(map(lambda x: MB(x), range(1, 2501)))
        ftuple_of_mb_int = FTuple(map(lambda x: MB(x), range(1, 2501)))
        dqueue_of_mb_int = DoubleQueue(map(lambda x: MB(x), range(1, 2501)))

        mb_list_int = sequence_mb(list_of_mb_int)
        mb_tuple_int = sequence_mb(tuple_of_mb_int)
        mb_ftuple_int = sequence_mb(ftuple_of_mb_int)
        mb_dqueue_int = sequence_mb(dqueue_of_mb_int)

        assert mb_list_int == MB(list(range(1, 2501)))
        assert mb_tuple_int == MB(tuple(range(1, 2501)))
        assert mb_ftuple_int == MB(FTuple(range(1, 2501)))
        assert mb_dqueue_int == MB(DoubleQueue(range(1, 2501)))

    def test_with_empties(self) -> None:
        list_of_mb_int = [MB(), MB(2), MB(3), MB(4)]
        tuple_of_mb_int = MB(1), MB[int](), MB(3), MB(4)
        ftuple_of_mb_int = FT(MB(1), MB(2), MB(), MB(4))
        dqueue_of_mb_int = DQ(MB(1), MB(2), MB(3), MB())

        mb_list_int = sequence_mb(list_of_mb_int)
        mb_tuple_int = sequence_mb(tuple_of_mb_int)
        mb_ftuple_int = sequence_mb(ftuple_of_mb_int)
        mb_dqueue_int = sequence_mb(dqueue_of_mb_int)

        assert mb_list_int == MB()
        assert mb_tuple_int == MB()
        assert mb_ftuple_int == MB()
        assert mb_dqueue_int == MB()

class TestXOR_sequence:
    def test_no_rights(self) -> None:
        list_of_xor_int_str = list(map(lambda x: XOR(x, str(x)), range(1, 2501)))
        tuple_of_xor_int_str = tuple(map(lambda x: XOR(x, str(x)), range(1, 2501)))
        ftuple_of_xor_int_str = FTuple(map(lambda x: XOR(x, str(x)), range(1, 2501)))
        dqueue_of_xor_int_str = DoubleQueue(map(lambda x: XOR(x, str(x)), range(1, 2501)))

        xor_listInt_str = sequence_xor(list_of_xor_int_str)
        xor_tupleInt_str = sequence_xor(tuple_of_xor_int_str)
        xor_ftupleInt_str: XOR[FTuple[int], str] = sequence_xor(ftuple_of_xor_int_str)
        xor_dqueueInt_str: XOR[DoubleQueue[int], str] = sequence_xor(dqueue_of_xor_int_str)

        assert xor_listInt_str == XOR(list(range(1, 2501)), 'does not matter')
        assert xor_tupleInt_str == XOR(tuple(range(1, 2501)), 'for this test')
        assert xor_ftupleInt_str == XOR(FTuple(range(1, 2501)), 'all are right')
        assert xor_dqueueInt_str == XOR(DoubleQueue(range(1, 2501)), 'none are wrong')

    def test_with_rights(self) -> None:
        list_of_xor_int_str: list[XOR[int, str]] = [XOR(right='1'), XOR(2), XOR(3), XOR(4)]
        tuple_of_xor_int_str: tuple[XOR[int, str], ...] = XOR(1), XOR(right='2'), XOR(3), XOR(4)
        ftuple_of_xor_int_str = FT(XOR(1, '1'), XOR(2, '2'), XOR(right='3'), XOR(4, '4'))
        dqueue_of_xor_int_str = DQ(XOR(1, '1'), XOR(2, '2'), XOR(3, '3'), XOR(right='4'))

        xor_list_int = sequence_xor(list_of_xor_int_str)
        xor_tuple_int = sequence_xor(tuple_of_xor_int_str)
        xor_ftuple_int = sequence_xor(ftuple_of_xor_int_str)
        xor_dqueue_int = sequence_xor(dqueue_of_xor_int_str)

        assert xor_list_int == XOR(right='1')
        assert xor_tuple_int == XOR(right='2')
        assert xor_ftuple_int == XOR(right='3')
        assert xor_dqueue_int == XOR(right='4')
        assert xor_dqueue_int != XOR(right='42')

