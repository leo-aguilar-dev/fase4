import logging
import os

LOG_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIRECTORY, "software_fj.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_NAME = "software_fj"


def get_logger(module_name=None):
    """Devuelve un logger que escribe en el archivo de logs y en consola.

    Se configura una sola vez; las siguientes llamadas reutilizan los mismos handlers.
    """
    logger_name = f"{LOGGER_NAME}.{module_name}" if module_name else LOGGER_NAME
    root_logger = logging.getLogger(LOGGER_NAME)

    if not root_logger.handlers:
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    return logging.getLogger(logger_name)


def log_error(logger, error, context=""):
    """Registra un error incluyendo su causa original si fue encadenado con 'raise ... from ...'."""
    message = f"{context}: {error}" if context else str(error)
    if error.__cause__ is not None:
        message += f" | Causa original: {type(error.__cause__).__name__}: {error.__cause__}"
    logger.error(message)
