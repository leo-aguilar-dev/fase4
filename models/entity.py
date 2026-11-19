from abc import ABC, abstractmethod
from datetime import datetime


class Entity(ABC):
    """Clase abstracta base para todas las entidades del sistema (Cliente, Reserva, etc.)."""

    def __init__(self, entity_id):
        self._id = entity_id
        self._created_at = datetime.now()

    def get_id(self):
        return self._id

    def get_created_at(self):
        return self._created_at

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def get_description(self):
        pass
