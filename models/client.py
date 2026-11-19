import re

from models.entity import Entity
from models.exceptions import InvalidDataError, MissingParameterError
from utils.logger import get_logger

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 60
PHONE_MIN_DIGITS = 7
PHONE_MAX_DIGITS = 15
NAME_PATTERN = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")

logger = get_logger("client")


class Client(Entity):
    """Cliente de Software FJ. Sus datos personales son privados y se validan al guardarlos."""

    def __init__(self, entity_id, name, email, phone):
        super().__init__(entity_id)
        self.__name = self._clean_name(name)
        self.__email = self._clean_email(email)
        self.__phone = self._clean_phone(phone)
        self.validate()
        logger.info(f"Cliente {self.get_id()} registrado")

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_phone(self):
        return self.__phone

    def set_name(self, name):
        self.__name = self._clean_name(name)
        logger.info(f"Cliente {self.get_id()}: nombre actualizado")

    def set_email(self, email):
        self.__email = self._clean_email(email)
        logger.info(f"Cliente {self.get_id()}: correo actualizado")

    def set_phone(self, phone):
        self.__phone = self._clean_phone(phone)
        logger.info(f"Cliente {self.get_id()}: teléfono actualizado")

    def validate(self):
        """Revisa que el cliente completo siga siendo válido."""
        if not isinstance(self.get_id(), str) or self.get_id().strip() == "":
            raise MissingParameterError("entity_id")
        self._clean_name(self.__name)
        self._clean_email(self.__email)
        self._clean_phone(self.__phone)

    def get_description(self):
        return f"Cliente [{self.get_id()}]: {self.__name} ({self.__email})"

    @staticmethod
    def _require_text(value, parameter_name):
        """Falla si el dato falta o no es texto; devuelve el texto sin espacios sobrantes."""
        if value is None:
            raise MissingParameterError(parameter_name)
        if not isinstance(value, str):
            raise InvalidDataError(f"El campo '{parameter_name}' debe ser texto")
        text = value.strip()
        if text == "":
            raise MissingParameterError(parameter_name)
        return text

    @staticmethod
    def _clean_name(name):
        text = Client._require_text(name, "name")
        if not NAME_MIN_LENGTH <= len(text) <= NAME_MAX_LENGTH:
            raise InvalidDataError(
                f"El nombre debe tener entre {NAME_MIN_LENGTH} y {NAME_MAX_LENGTH} caracteres"
            )
        if NAME_PATTERN.match(text) is None:
            raise InvalidDataError(f"El nombre solo puede tener letras y espacios: '{text}'")
        return text

    @staticmethod
    def _clean_email(email):
        text = Client._require_text(email, "email")
        if EMAIL_PATTERN.match(text) is None:
            raise InvalidDataError(f"Correo electrónico inválido: '{text}'")
        return text.lower()

    @staticmethod
    def _clean_phone(phone):
        text = Client._require_text(phone, "phone")
        digits = text.replace(" ", "").replace("-", "")
        if digits.startswith("+"):
            digits = digits[1:]
        try:
            int(digits)
        except ValueError as error:
            raise InvalidDataError(f"El teléfono solo puede tener números: '{text}'") from error
        if not digits.isdigit() or not PHONE_MIN_DIGITS <= len(digits) <= PHONE_MAX_DIGITS:
            raise InvalidDataError(
                f"El teléfono debe tener entre {PHONE_MIN_DIGITS} y {PHONE_MAX_DIGITS} dígitos: '{text}'"
            )
        return text

    def __str__(self):
        return self.get_description()
