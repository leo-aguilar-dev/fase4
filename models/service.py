from abc import ABC, abstractmethod

class Service(ABC):
    def __init__(self, name, cost):
        self._name = name
        self._cost = cost

    def get_name(self):
        return self._name

    def get_cost(self):
        return self._cost

    def set_cost(self, cost):
        if cost < 0:
            raise ValueError("El costo no puede ser negativo")
        self._cost = float(cost)
        
    @abstractmethod
    def calculate_cost(self):
        pass
    
    @abstractmethod
    def get_description(self):
        pass
    
    @abstractmethod
    def validate(self):
        pass