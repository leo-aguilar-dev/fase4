from abc import ABC, abstractmethod
from models.entity import Entity
from models.exceptions import InvalidDataError, MissingParameterError

class Service(Entity, ABC):
    def __init__(self, entity_id, name, cost):
        super().__init__(entity_id)
        if not isinstance(name, str) or not name.strip():
            raise MissingParameterError("name")
        self._name = name.strip()
        self._cost = cost

    def get_name(self):
        return self._name

    def get_cost(self):
        return self._cost

    def set_cost(self, cost):
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            raise InvalidDataError("El costo debe ser un número válido")
        if cost < 0:
            raise InvalidDataError("El costo no puede ser negativo")
        self._cost = float(cost)
        
    @abstractmethod
    def calculate_cost(self, duration, units=None):
        pass
    
    @abstractmethod
    def get_description(self):
        pass
    
    @abstractmethod
    def validate(self, units=None):
        pass