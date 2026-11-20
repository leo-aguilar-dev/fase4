from abc import ABC, abstractmethod
from datetime import datetime
from models.exceptions import MissingParameterError


class Entity(ABC):
    """Clase abstracta base para las entidades del sistema de Software FJ."""

    def __init__(self, entity_id):
        if entity_id is None or str(entity_id).strip() == "":
            raise MissingParameterError("El identificador de la entidad no puede estar vacío")
        self._id = str(entity_id).strip()
        self._created_at = datetime.now()

    def get_id(self):
        """Retorna el identificador único de la entidad."""
        return self._id
    
    def get_created_at(self):
        """Retorna la fecha y hora de creación de la entidad."""
        return self._created_at

    @abstractmethod
    def validate(self):
        """Valida que los datos de la entidad sean correctos."""

    @abstractmethod
    def get_description(self):
        """Retorna una descripción general de la entidad."""
