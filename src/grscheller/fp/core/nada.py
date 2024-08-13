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

"""
### Module level sentinel value

* sentinel value _nada: _Nada
  * final variable with a singular value
  * keep inaccessible to client code
  * not to be exported

"""

from __future__ import annotations

__all__ = ['_nada', '_Nada']

from typing import Final

_Nada = tuple[None, tuple[None, tuple[None, tuple[None, None]]]]
_nada: Final[_Nada] = None, (None, (None, (None, None)))














