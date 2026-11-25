# SPDX-License-Identifier: MIT

import logging
import sys
from pathlib import Path

from gselib.deps import available, require
from gselib.converters.formats import ConverterRegistry, FORMAT_EXT, normalise

__all__ = ["add_converters_subparser", "run_converters_command"]

_log = logging.getLogger(__name__)


def _output_is_file(output: Path, target: str) -> bool:
    return normalise(output.suffix) == target


def add_converters_subparser(subparsers) -> None:
    """Register the convert subcommand on the given subparsers."""
    if not available("converters"):
        return

    convert = subparsers.add_parser("convert", help="convert detector image formats")
    convert.add_argument("--source", "-s", required=True, metavar="FORMAT", help="source format, e.g. .h5 or hdf5")
    convert.add_argument("--target", "-t", required=True, metavar="FORMAT", help="target format, e.g. .cbf")
    convert.add_argument("--file", "-f", required=True, metavar="PATH", help="source file or directory")
    convert.add_argument("--output", "-o", metavar="DIR", help="output directory or file path (default: {source_dir}/{target}/)")
    convert.add_argument("--width", "-w", type=int, default=3, metavar="N", help="zero padding width for frame index suffix (default: 3 -> _000)")


@require("converters")
def run_converters_command(args) -> None:
    """Dispatches a parsed convert command to the per-format converter."""
    source = normalise(args.source)
    target = normalise(args.target)
    provided_path = Path(args.file)
    output = Path(args.output) if args.output else None
    width = args.width

    try:
        converter = ConverterRegistry.get(target)
    except KeyError as e:
        sys.exit(f"error: {e}")

    kwargs = dict(source_format=source, frame_number_width=width)

    if provided_path.is_file():
        if output and _output_is_file(output=output, target=target):
            converter(directory=provided_path.parent, basename=provided_path.stem, output_dir=output.parent, output_name=output.name, **kwargs)
        else:
            converter(directory=provided_path.parent, basename=provided_path.stem, output_dir=output or provided_path.parent / target, **kwargs)

    elif provided_path.is_dir():
        if output and _output_is_file(output=output, target=target):
            sys.exit("error: --output must be a directory when --file is a directory")

        exts = FORMAT_EXT.get(source, [source])
        sources = sorted(f for ext in exts for f in provided_path.glob(f"*.{ext}"))
        if not sources:
            sys.exit(f"error: no {source} files found in {provided_path}")

        out_dir = output or provided_path / target
        for source_file in sources:
            converter(directory=provided_path, basename=source_file.stem, output_dir=out_dir, **kwargs)

    else:
        sys.exit(f"error: {args.file!r} is not a file or directory")
