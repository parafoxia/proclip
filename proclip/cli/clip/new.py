# Copyright (c) 2021-present, Ethan Henderson
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

import click

from proclip import CONFIG_DIR, ux
from proclip.api import Clip
from proclip.cli.clip import cmd_clip


@cmd_clip.command(name="new", help="Create a new clip called NAME from file FILE.")
@click.argument("name")
@click.argument("file", type=Path)
@click.option(
    "-o",
    "--output-dir",
    type=Path,
    help=(
        "The directory this clip should be saved to. If this is not provided, the clip "
        f"will be saved to '{CONFIG_DIR}'."
    ),
)
def cmd_clip_new(name: str, file: Path, output_dir: Path | None) -> None:
    try:
        clip = Clip(name, file.read_bytes(), file.suffix)

        if not output_dir:
            CONFIG_DIR.mkdir(exist_ok=True)
            output_dir = CONFIG_DIR

        clip.write(to_dir=output_dir)
        ux.cprint("aok", "Success!")

    except Exception as exc:
        ux.cprint("err", f"{exc}")
