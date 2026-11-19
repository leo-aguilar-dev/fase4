from abc import ABC, abstractmethod


class Entity(ABC):
    """Clase abstracta base para las entidades del sistema de Software FJ."""

    def __init__(self, entity_id):
        if not isinstance(entity_id, str) or entity_id.strip() == "":
            raise ValueError("El identificador de la entidad no puede estar vacío")
        self._entity_id = entity_id.strip()

    def get_id(self):
        """Retorna el identificador único de la entidad."""
        return self._entity_id

    @abstractmethod
    def validate(self):
        """Valida que los datos de la entidad sean correctos."""

    @abstractmethod
    def get_description(self):
        """Retorna una descripción general de la entidad."""

    def __str__(self):
        return self.get_description()
