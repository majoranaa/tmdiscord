from __future__ import annotations

import google.cloud.logging
import loguru
from loguru import logger as loguru_logger

from enum import Enum
import functools
import itertools
import logging
from typing import Any

import sys

# opt() will not preserve previous options.
# https://loguru.readthedocs.io/en/stable/resources/recipes.html#preserving-an-opt-parameter-for-the-whole-module
LOGURU_OPTIONS = {"capture": False}
logger = loguru_logger.opt(**LOGURU_OPTIONS)
logger.opt = functools.partial(logger.opt, **LOGURU_OPTIONS)


class LoguruFilter(logging.Filter):
    """Adapts loguru records to standard library logging LogRecord.

    Refer to https://github.com/Delgan/loguru/issues/271
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if "extra" not in record.__dict__:
            return True
        extra: dict[str, Any] = record.__dict__["extra"]
        del record.__dict__["extra"]
        for key, value in extra.items():
            if "json_fields" not in record.__dict__:
                record.__dict__["json_fields"] = {}
            record.__dict__["json_fields"][key] = value
        return True


class LoguruFormatter:
    """Formats a loguru record to a string.

    Based on the default loguru format, but also prints all key-value pairs in the extra field as
    logfmt. Since Google Cloud Logging also specifies a json_fields key for user-specific fields,
    these are extracted separately.
    """

    def __call__(self, record: loguru.Record) -> str:
        # Based on loguru._defaults.LOGURU_FORMAT
        base = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        extra = record["extra"]
        has_extra = False
        processed = {"json_fields"}
        json_fields: dict[str, Any] = extra["json_fields"] if "json_fields" in extra else {}
        for key, value in itertools.chain(json_fields.items(), extra.items()):
            if key in processed:
                continue
            processed.add(key)
            if not has_extra:
                has_extra = True
                base = f"{base}  "
            base = f"{base} <yellow>{key}</yellow>={value}"

        return base + "\n{exception}"


class LoggingEnvironment(str, Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"


class LoggingLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class __LoggingConfiguration:
    """Configures logging, which uses both loguru and standard library logging.

    Records if logging has been configured, which should only occur once. Is singleton and
    module-private to ensure it is only used via the instance exposed by this module.
    """

    instance = None

    def __new__(cls) -> __LoggingConfiguration:
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.__is_configured = False

    def is_configured(self) -> bool:
        return self.__is_configured

    def configure_logger(self, env: LoggingEnvironment, level: LoggingLevel, filename: str) -> None:
        if self.__is_configured:
            return
        else:
            self.__is_configured = True

        logger.remove()
        if env == LoggingEnvironment.CLOUD:
            cloud_logging_client = google.cloud.logging.Client()
            handler = cloud_logging_client.get_default_handler()
            handler.addFilter(LoguruFilter())
            logger.add(handler, level=level.name, format="{message}")
        else:  # LoggingEnvironment.LOCAL
            logger.add(sys.stderr, level=level.name, format=LoguruFormatter())
            cloud_logging_client = google.cloud.logging.Client()
            # StructuredLogHandler inherits from StreamHandler, which should close the log file.
            handler = google.cloud.logging.handlers.StructuredLogHandler(
                stream=open(filename, "w"), project_id=cloud_logging_client.project
            )
            handler.addFilter(LoguruFilter())
            logger.add(handler, level=level.name, format="{message}")
        logger.info(f"Configured logger for {env.name} env.")


__logging_configuration = __LoggingConfiguration()

is_configured = __logging_configuration.is_configured
configure_logger = __logging_configuration.configure_logger
