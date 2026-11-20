from models.service import Service
from models.exceptions import InvalidDataError

class ReserveRoom(Service):
    def __init__(self, entity_id, name, cost, room_number):
        super().__init__(entity_id, name, cost)
        self.room_number = room_number
        self.validate()

    def calculate_cost(self, duration, units=None):
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration <= 0:
            raise InvalidDataError("La duración debe ser un número válido")
        return round(self.get_cost() * duration, 2)

    def get_description(self):
        return f"Reservar sala '{self.get_name()}' (Sala #{self.room_number})"

    def validate(self, units=None):
        if isinstance(self.room_number, bool) or not isinstance(self.room_number, int) or self.room_number <= 0:
            raise InvalidDataError("El número de sala debe ser un entero positivo")