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

import click

from proclip import CONFIG_DIR, ux
from proclip.api import Clip
from proclip.cli.clip import cmd_clip


@cmd_clip.command(name="paste", help="Paste a clip of name NAME to a file.")
@click.argument("name")
@click.option(
    "-i",
    "--input-dir",
    type=Path,
    help=(
        "The directory to load the clip from. IF this is not provided, the clip will "
        f"be loaded from '{CONFIG_DIR}'."
    ),
)
@click.option(
    "-o",
    "--output",
    type=Path,
    help=(
        "The file this clip should be written to. This can be a file or a directory. "
        "If this is a directory, the name and suffix will be automatically populated. "
        "If this is not provided, the clip will be written to the current working "
        "directory."
    ),
)
@click.option(
    "-v",
    "--variables",
    help="The variables to pass to the clip.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Whether to overwrite an existing file on conflict.",
)
def cmd_clip_paste(
    name: str,
    input_dir: Path | None,
    output: Path | None,
    variables: str | None,
    overwrite: bool,
) -> None:
    try:
        if not input_dir:
            CONFIG_DIR.mkdir(exist_ok=True)
            input_dir = CONFIG_DIR

        clip = Clip.read(name, from_dir=input_dir)

        if not output:
            output = Path.cwd() / f"{name}{clip.suffix}"

        if output.is_dir():
            output /= f"{name}{clip.suffix}"

        if output.exists() and not overwrite:
            raise FileExistsError("A file with that name already exists.")

        clip.paste(variables, to_file=output)
        ux.cprint("aok", "Success!")

    except Exception as exc:
        ux.cprint("err", f"{exc}")
