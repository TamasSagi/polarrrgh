import logging
import sys
import traceback
from datetime import datetime
from io import StringIO
from pathlib import Path
from types import TracebackType
from typing import Type

from polarrrgh.logger.config import LoggerConfig


class CLIColorFmt(logging.Formatter):
    COLOR_MAP = {
        logging.DEBUG: "\x1b[2;49;90m{}\x1b[0m",
        logging.INFO: "\x1b[38;20m{}\x1b[0m",
        logging.WARNING: "\x1b[33;20m{}\x1b[0m",
        logging.ERROR: "\x1b[31;20m{}\x1b[0m",
        logging.CRITICAL: "\x1b[31;1m{}\x1b[0m",
    }

    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style="%",
        validate=True,
        *,
        defaults=None,
        formatter: logging.Formatter,
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.formats = {
            level: format.format(formatter._fmt)
            for level, format in self.COLOR_MAP.items()
        }

    def format(self, record: logging.LogRecord) -> str:
        if record.exc_info:
            record.msg += self.formatException(record.exc_info)
            record.exc_info = None

        return logging.Formatter(self.formats.get(record.levelno)).format(record)


class Handler(logging.Handler):
    """
    Handles logging from multiple processes using a shared queue.
    """

    def __init__(self, config: LoggerConfig):
        logging.Handler.__init__(self)

        self.config = config
        self.handlers = self.create_handlers()

        # Set capture warnings
        logging.captureWarnings(self.config.capture_warnings)

        # Set capture exceptions
        if self.config.capture_exceptions:
            sys.excepthook = self._handle_exc

    def create_stream_handler(self) -> logging.StreamHandler:
        formatter = self.config.formatter

        if self.config.colored:
            formatter = CLIColorFmt(formatter=self.config.formatter)

        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.getLevelName(self.config.console_level.upper()))
        s_handler.setFormatter(formatter)

        return s_handler

    def create_file_handler(self) -> logging.FileHandler:
        if self.config.file_name:
            path = Path.cwd() / self.config.file_name
        else:
            dtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = Path.cwd() / f"{dtime}.log"

        f_handler = logging.FileHandler(path, encoding=self.config.encoding, delay=True)
        f_handler.setFormatter(self.config.formatter)
        f_handler.setLevel(logging.getLevelName(self.config.file_level.upper()))

        return f_handler

    def create_handlers(self) -> list[logging.Handler]:
        return [self.create_stream_handler(), self.create_file_handler()]

    def _handle_exc(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        sio = StringIO()
        traceback.print_exception(exc_type, exc_value, exc_tb, limit=None, file=sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]

        tb_info = traceback.extract_tb(exc_tb, 1)[0]
        record = logging.LogRecord(
            tb_info.name,
            logging.ERROR,
            tb_info.filename,
            tb_info.lineno,
            s,
            [],
            None,
        )

        self.emit(record)
        self.close()

    def emit(self, record: logging.LogRecord) -> None:
        for handler in self.handlers:
            if handler.level <= record.levelno:
                handler.emit(record)
