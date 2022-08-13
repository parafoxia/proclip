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

__all__ = ("Clip",)

import re
import typing as t
from dataclasses import dataclass
from pathlib import Path

from proclip.errors import UnsupportedFile

if t.TYPE_CHECKING:
    from proclip.types import PathLikeT

_SPEC_ID = b"\x99\x69"
_VAR_PATTERN = re.compile(r"{{ *([A-Za-z0-9_]+) *=? *([A-Za-z0-9_]*)? *}}")


@dataclass(init=False)
class Clip:
    __slots__ = ("_name", "_content", "_suffix", "_variables")

    def __init__(
        self,
        name: str,
        content: bytes,
        suffix: str,
        *,
        variables: dict[str, str] | None = None,
    ) -> None:
        self._name = name
        self._content = content
        self._suffix = suffix
        self._variables = (
            variables if variables else self._find_variables(self._content)
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def variables(self) -> dict[str, str]:
        return self._variables

    @staticmethod
    def _header_for(x: str | bytes, n: int) -> str:
        if len(x) > 16**n - 1:
            raise ValueError(f"datum of size {len(x)} not supported in this context")

        return f"{hex(len(x))[2:]:>0{n}}"

    @staticmethod
    def _find_variables(content: bytes) -> dict[str, str]:
        matches: list[tuple[str, str]] = _VAR_PATTERN.findall(content.decode("utf-8"))
        return dict(sorted(matches, key=lambda x: x[1]))

    @staticmethod
    def _parse_variables(body: str) -> dict[str, str]:
        return dict(var.split("=") for var in body.split(","))

    def _transform_content(self, vars: dict[str, str]) -> bytes:
        content = self.content.decode("utf-8")

        while True:
            match = _VAR_PATTERN.search(content)
            if not match:
                break
            content = (
                f"{content[:match.start()]}"
                f"{vars[match.group(1)]}"
                f"{content[match.end():]}"
            )

        return content.encode("utf-8")

    @classmethod
    def read(cls, name: str, *, from_dir: PathLikeT) -> Clip:
        if not isinstance(from_dir, Path):
            from_dir = Path(from_dir)

        with open(from_dir / f"{name}.clip", "rb") as f:
            if f.read(2) != _SPEC_ID:
                raise UnsupportedFile("The provided file is not a valid clip file.")

            # Skip over headers.
            f.read(4)

            # Read suffix.
            size = int(f.read(2).decode("utf-8"), base=16)
            suffix = f.read(size).decode("utf-8")

            # Read content (and convert to work on Windows).
            size = int(f.read(8).decode("utf-8"), base=16)
            content = f.read(size).replace(b"\r\n", b"\n")

            # Read and parse variables.
            size = int(f.read(8).decode("utf-8"), base=16)
            if size:
                vars = cls._parse_variables(f.read(size).decode("utf-8"))
            else:
                vars = {}

        return cls(name, content, suffix, variables=vars)

    def write(self, *, to_file: PathLikeT) -> Path:
        if not isinstance(to_file, Path):
            to_file = Path(to_file)

        with open(to_file, "wb") as f:
            # Identification.
            f.write(_SPEC_ID)

            # Reserved space for headers.
            f.write(b"0000")

            # Write suffix.
            f.write(f"{self._header_for(self.suffix, 2)}{self.suffix}".encode("utf-8"))

            # Write content.
            f.write(self._header_for(self.content, 8).encode("utf-8"))
            f.write(self.content)

            # Find and write variables.
            var_list = ",".join(f"{k}={v}" for k, v in self.variables.items())
            h = self._header_for(var_list, 8)
            f.write(f"{h}{var_list}".encode())

        return to_file

    def paste(self, variables: str | None, *, to_file: PathLikeT) -> Path:
        if not isinstance(to_file, Path):
            to_file = Path(to_file)

        vars = self.variables.copy()
        if variables:
            vars.update(self._parse_variables(variables))

        if not all(v for v in vars.values()):
            raise ValueError("Some variables do not have values.")

        with open(to_file, "wb") as f:
            f.write(self._transform_content(vars))

        return to_file
