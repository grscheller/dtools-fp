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
from dtools.containers.tuples.ftuple import FTuple as FT, f_tuple as ft
from dtools.queues.de import DEQueue as DQ, de_queue as dq
from dtools.fp.err_handling import MayBe as MB
from dtools.fp.err_handling import Xor, LEFT, RIGHT


class Test_MB_sequence:
    """Test MayBe sequence class function"""

    def test_no_empties(self) -> None:
        """Test without empty MayBe values"""
        list_mb_int = list(map(MB, range(1, 2501)))
        tuple_mb_int = tuple(map(MB, range(1, 2501)))
        ftuple_mb_int = FT(map(MB, range(1, 2501)))
        dqueue_mb_int = DQ(map(MB, range(1, 2501)))

        mb_list_int = MB.sequence(list_mb_int).map(list)
        mb_tuple_int = MB.sequence(tuple_mb_int).map(tuple)
        mb_ftuple_int = MB.sequence(ftuple_mb_int).map(FT)
        mb_dqueue_int = MB.sequence(dqueue_mb_int).map(DQ)

        assert mb_list_int == MB(list(range(1, 2501)))
        assert mb_tuple_int == MB(tuple(range(1, 2501)))
        assert mb_ftuple_int == MB(FT(range(1, 2501)))
        assert mb_dqueue_int == MB(DQ(range(1, 2501)))

    def test_with_empties(self) -> None:
        """Test with empty MayBe values"""
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


class Test_Xor_sequence:
    """Test Xor sequence class function"""

    def test_no_rights(self) -> None:
        """Test with omly left values"""
        list_of_xor_int_str: list[Xor[int, str]] = list(
            map(lambda x: Xor(x, LEFT), range(1, 2501))
        )
        tuple_of_xor_int_str: tuple[Xor[int, str], ...] = tuple(
            map(lambda x: Xor(x, LEFT), range(1, 2501))
        )
        ftuple_of_xor_int_str: FT[Xor[int, str]] = FT(
            map(lambda x: Xor(x, LEFT), range(1, 2501))
        )
        dqueue_of_xor_int_str: DQ[Xor[int, str]] = DQ(
            map(lambda x: Xor(x, LEFT), range(1, 2501))
        )

        xor_listInt_str: Xor[list[int], str] = Xor.sequence(
            list_of_xor_int_str
        ).map(list, '')
        xor_tupleInt_str: Xor[tuple[int, ...], str] = Xor.sequence(
            tuple_of_xor_int_str
        ).map(tuple, '')
        xor_ftuple_int_str: Xor[FT[int], str] = Xor.sequence(
            ftuple_of_xor_int_str
        ).map(FT, '')
        xor_dqueue_int_str: Xor[DQ[int], str] = Xor.sequence(
            dqueue_of_xor_int_str
        ).map(DQ, '')

        assert xor_listInt_str == Xor(list(range(1, 2501)), LEFT)
        assert xor_tupleInt_str == Xor(tuple(range(1, 2501)), LEFT)
        assert xor_ftuple_int_str == Xor(FT(range(1, 2501)), LEFT)
        assert xor_dqueue_int_str == Xor(DQ(range(1, 2501)), LEFT)

    def test_with_a_right(self) -> None:
        """Test with a single right value, use multiple data structures"""
        list_of_xor_int_str: list[Xor[int, str]] = [
            Xor('1', RIGHT), Xor(2, LEFT), Xor(3, LEFT), Xor(4, LEFT)
        ]
        tuple_of_xor_int_str: tuple[Xor[int, str], ...] = (
            Xor(1, LEFT), Xor('2', RIGHT), Xor(3, LEFT), Xor(4, LEFT)
        )
        ftuple_of_xor_int_str = ft(
            Xor(1, LEFT), Xor(2, LEFT), Xor('3', RIGHT), Xor(4, LEFT)
        )
        dqueue_of_xor_int_str = dq(
            Xor(1, LEFT), Xor(2, LEFT), Xor(3, LEFT), Xor('4', RIGHT)
        )

        xor_list_int = Xor.sequence(list_of_xor_int_str).map(list, 'No!')
        xor_tuple_int = Xor.sequence(tuple_of_xor_int_str).map(tuple, 'No!')
        xor_ftuple_int = Xor.sequence(ftuple_of_xor_int_str).map(FT, 'No!')
        xor_dqueue_int = Xor.sequence(dqueue_of_xor_int_str).map(DQ, 'No!')

        assert xor_list_int == Xor('1', RIGHT)
        assert xor_tuple_int == Xor('2', RIGHT)
        assert xor_ftuple_int == Xor('3', RIGHT)
        assert xor_dqueue_int == Xor('4', RIGHT)

    def test_with_multiple_rights(self) -> None:
        """Test with a multiple right value"""

        type Letter = Xor[str, int]
        type Letters = Xor[list[str], int]

        ALPHABET: Final[str] = ' abcdefghijklmnopqrstuvwxyz'

        def alphabet_position(char_str: str) -> int:
            """Letter position in ALPHABET"""
            char = ' '
            if len(char_str):
                char = char_str[0]
            if 0 < (pos := ord(char) - 96) < 27:
                return pos
            return 0

        def letter_left(letter: str) -> Letter:
            pos = alphabet_position(letter)
            return Xor(ALPHABET[pos], LEFT)

        def letter_right(letter: str) -> Letter:
            pos = alphabet_position(letter)
            return Xor(pos, RIGHT)

        letter_set_0 = list[str]()
        letter_set_1 = ['a', 'w', 's', 's', 'b', 'm', 'j']
#       letter_set_2 = ['w', 'x', 'y', 'z', ' ']
#       letter_set_3 = ['waldo', 'x', 'y', 'zebra', '']

        data0 = list(map(letter_left, letter_set_0))
        data1 = list(map(letter_left, letter_set_1))
        data2 = list(data1)
        data2[5] = data2[5].bind(letter_right, 0)

        sequenced_data0 = Xor.sequence(data0).map(list, 2)
        sequenced_data1 = Xor.sequence(data1).map(list, 0)
        sequenced_data2: Letters = Xor.sequence(data2).map(list, -2)

        result0: Letters = Xor([], LEFT)
        result1: Letters = Xor(letter_set_1, LEFT)
        result2: Letters = Xor(13, RIGHT)

        assert sequenced_data0 == result0
        assert sequenced_data1 == result1
        assert sequenced_data2 == result2
