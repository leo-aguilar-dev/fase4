from models.exceptions import InvalidDataError, MissingParameterError
from models.service import Service


class SpecializedConsulting(Service):
    def __init__(self, entity_id, name, cost, consultant_name):
        super().__init__(entity_id, name, cost)
        if consultant_name is None or not isinstance(consultant_name, str) or not consultant_name.strip():
            raise MissingParameterError("consultant_name")
        self.consultant_name = consultant_name.strip()
        self.validate()

    def calculate_cost(self, duration, units=None):
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration <= 0:
            raise InvalidDataError("El número de horas debe ser un número positivo")
        return round(self.get_cost() * duration, 2)

    def get_description(self):
        return f"Consultoría especializada '{self.get_name()}' con {self.consultant_name}"

    def validate(self, units=None):
        if not isinstance(self.consultant_name, str) or not self.consultant_name.strip():
            raise InvalidDataError("El nombre del consultor debe ser una cadena no vacía")