import logging

from polarrrgh.logger.config import LoggerConfig
from polarrrgh.logger.handler import Handler
from polarrrgh.logger.mproc_handler import MProcHandler


class MProcHandlerCtx:
    def __init__(self, config: LoggerConfig | None = None, mproc: bool = False):
        self.config = config if config else LoggerConfig.default()
        self.handler = MProcHandler(self.config) if mproc else Handler(self.config)

        logger = logging.getLogger(self.config.name)
        logger.setLevel(logging.DEBUG)

        # TODO: it should be restricted to add the same handler twice
        logger.addHandler(self.handler)

    def __enter__(self):
        return logging.getLogger(self.config.name)

    def __exit__(self, a, b, c):
        print(a, b, c)
        self.handler.close()


def get_logger(
    config: LoggerConfig | None = None, mproc: bool = False
) -> logging.Logger:
    config = config if config else LoggerConfig.default()
    handler = MProcHandler(config) if mproc else Handler(config)

    logger = logging.getLogger(config.name)
    logger.setLevel(logging.DEBUG)

    # TODO: it should be restricted to add the same handler twice
    logger.addHandler(handler)

    return logger


def close() -> None:
    for handler in logging.getLogger().handlers:
        if isinstance(handler, MProcHandler):
            handler.close()
