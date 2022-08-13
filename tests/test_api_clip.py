# Copyright (c) 2022-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

from pathlib import Path

import pytest

from proclip.api import Clip
from proclip.errors import UnsupportedFile

READ_DIR = Path(__file__).parent
WRITE_DIR = READ_DIR / "temp"


@pytest.fixture()
def clip() -> Clip:
    return Clip(
        "mock_clip",
        b"print('{{ msg }}')\nsorted('{{ str = qwerty }}')\n",
        ".py",
        variables={"msg": "", "str": "qwerty"},
    )


def test_clip_properties(clip: Clip) -> None:
    assert clip.name == "mock_clip"
    assert clip.content == b"print('{{ msg }}')\nsorted('{{ str = qwerty }}')\n"
    assert clip.suffix == ".py"
    assert clip.variables == {"msg": "", "str": "qwerty"}


def test_create_header() -> None:
    header = Clip._header_for("hello world", 4)
    assert header == "000b"


def test_create_bad_header() -> None:
    with pytest.raises(ValueError) as exc:
        Clip._header_for("never gonna give you up", 1)
    assert str(exc.value) == "datum of size 23 not supported in this context"


def test_find_variables() -> None:
    content = b"{{ var1 }} {{ var2 = 5 }}"
    vars = Clip._find_variables(content)
    assert vars == {"var1": "", "var2": "5"}


def test_find_variables_no_spaces() -> None:
    content = b"{{var1}} {{var2=5}}"
    vars = Clip._find_variables(content)
    assert vars == {"var1": "", "var2": "5"}


def test_parse_variables() -> None:
    body = "var1=,var2=5"
    vars = Clip._parse_variables(body)
    assert vars == {"var1": "", "var2": "5"}


def test_transform_content(clip: Clip) -> None:
    vars = {"msg": "Hello world!", "str": "qwerty"}
    content = clip._transform_content(vars)
    assert content == b"print('Hello world!')\nsorted('qwerty')\n"


def test_read_from_file(clip: Clip) -> None:
    clip2 = Clip.read("mock_clip", from_dir=READ_DIR)
    assert clip.name == clip2.name
    assert clip.content == clip2.content
    assert clip.suffix == clip2.suffix
    assert clip.variables == clip2.variables


def test_read_from_str_file(clip: Clip) -> None:
    clip2 = Clip.read("mock_clip", from_dir=str(READ_DIR))
    assert clip.name == clip2.name
    assert clip.content == clip2.content
    assert clip.suffix == clip2.suffix
    assert clip.variables == clip2.variables


def test_read_from_bad_file() -> None:
    with pytest.raises(UnsupportedFile) as exc:
        Clip.read("bad_mock_clip", from_dir=READ_DIR)
    assert str(exc.value) == "The provided file is not a valid clip file."


def test_read_from_file_no_vars() -> None:
    clip = Clip.read("mock_clip_no_vars", from_dir=READ_DIR)
    assert clip.variables == {}


def test_write_to_file(clip: Clip) -> None:
    file = clip.write(to_file=WRITE_DIR / "mock_clip.clip")
    assert file.exists()


def test_write_to_str_file(clip: Clip) -> None:
    file = clip.write(to_file=str(WRITE_DIR / "mock_clip_str.clip"))
    assert file.exists()


def test_paste_to_file(clip: Clip) -> None:
    file = clip.paste("msg=Hello world!", to_file=WRITE_DIR / "mock_clip.py")
    assert file.exists()


def test_paste_to_str_file(clip: Clip) -> None:
    file = clip.paste("msg=Hello world!", to_file=str(WRITE_DIR / "mock_clip_str.py"))
    assert file.exists()


def test_paste_to_file_missing_vars(clip: Clip) -> None:
    with pytest.raises(ValueError) as exc:
        clip.paste(None, to_file=WRITE_DIR / "mock_clip_str.py")
    assert str(exc.value) == "Some variables do not have values."
