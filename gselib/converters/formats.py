# SPDX-License-Identifier: MIT

import importlib
from pathlib import Path
from typing import Protocol

__all__ = ["ConverterProtocol", "ConverterRegistry", "FORMAT_EXT", "normalise"]

# Extension mapping
FORMAT_EXT: dict[str, list[str]] = {
    "hdf5": ["h5", "hdf5"],
    "cbf": ["cbf"],
}

# Reverse extension mapping
EXT_TO_FORMAT: dict[str, str] = {ext: format for format, extensions in FORMAT_EXT.items() for ext in extensions}


def normalise(format: str) -> str:
    """Strip leading dot and lowercase."""
    key = format.lstrip(".").lower()
    return EXT_TO_FORMAT.get(key, key)


class ConverterProtocol(Protocol):
    def __call__(
        self, directory: Path | str, basename: str, source_format: str, output_dir: Path | str | None, output_name: str | None, frame_number_width: int
    ) -> None: ...


class ConverterRegistry:
    _registry: dict[str, tuple[str, str]] = {"cbf": ("gselib.converters.cbf_converter", "convert_to_cbf")}

    @classmethod
    def get(cls, target: str) -> ConverterProtocol:
        """Return the converter protocol for the target."""
        entry = cls._registry.get(target)
        if entry is None:
            supported = ", ".join(sorted(cls._registry))
            raise KeyError(f"no converter registered for {target!r} - supported: {supported}")
        module_path, func_name = entry
        return getattr(importlib.import_module(module_path), func_name)

    @classmethod
    def supported_targets(cls) -> list[str]:
        return sorted(cls._registry)
