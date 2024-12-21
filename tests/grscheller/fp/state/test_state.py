# Copyright 2024 Geoffrey R. Scheller
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

from grscheller.fp.state import State

class Test_simple:
    def test_counter(self) -> None:
        sc = State(lambda s: (s+1, s+1)) 

        aa, ss = sc.run(0)
        assert aa == 1
        assert ss == 1

        aa, ss = sc.run(42)
        assert aa == 43
        assert ss == 43

        sc1 = sc.flatmap(lambda a: sc)
        aa, ss = sc1.run(0)
        assert aa == 2
        assert ss == 2

        start: State[int, int] = State.set(0).get()
        sc2 = start.flatmap(lambda a: sc)
        aa, ss = sc2.run(0)
        assert aa == 1
        assert ss == 1

        sc3 = start.flatmap(lambda a: sc).flatmap(lambda a: sc)
        aa, ss = sc1.run(0)
        assert aa == 2
        assert ss == 2

