import logging
import sys

_LEVEL_COLORS = {
    logging.DEBUG: "\x1b[90m",
    logging.INFO: "\x1b[37m",
    logging.WARNING: "\x1b[33m",
    logging.ERROR: "\x1b[31m",
    logging.CRITICAL: "\x1b[91m",
}
_RESET = "\x1b[0m"


class _SMREFormatter(logging.Formatter):
    def format(self, record):
        color = _LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        if sys.stdout.isatty():
            return f"{color}{message}{_RESET}"
        return message


def _build_logger():
    logger = logging.getLogger("smre")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_SMREFormatter("[SMRE] %(levelname)s: %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = _build_logger()


def set_level(level):
    logger.setLevel(level)


def debug(message, *args):
    logger.debug(message, *args)


def info(message, *args):
    logger.info(message, *args)


def warning(message, *args):
    logger.warning(message, *args)


def error(message, *args):
    logger.error(message, *args)


def critical(message, *args):
    logger.critical(message, *args)
