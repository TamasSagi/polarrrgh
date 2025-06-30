from __future__ import annotations

import logging
from pathlib import Path
from typing import Type

import msgspec


class LoggerConfig(msgspec.Struct):
    name: str | None
    formatter: logging.Formatter | None
    colored: bool
    encoding: str
    capture_exceptions: bool
    capture_warnings: bool

    console_level: str | int

    file_level: str | int
    file_name: str | None

    @classmethod
    def default(cls: Type[LoggerConfig]) -> LoggerConfig:
        return cls(
            name=None,
            formatter=logging.Formatter(
                "[%(asctime)s %(filename)24s:%(lineno)4s](%(process)6d) - %(levelname)-8s - %(message)s"
            ),
            colored=True,
            encoding="utf-8",
            capture_exceptions=True,
            capture_warnings=True,
            console_level="debug",
            file_level="debug",
            file_name=None,
        )

    @classmethod
    def from_json(cls: Type[LoggerConfig], path: Path) -> LoggerConfig:
        raise NotImplementedError