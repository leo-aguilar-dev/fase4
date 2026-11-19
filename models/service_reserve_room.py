from service import Service

class ReserveRoom(Service):
    def __init__(self, name, cost, room_number):
        super().__init__(name, cost)
        self.room_number = room_number

    def calculate_cost(self, hours):
        if hours < 0:
            raise ValueError("El número de horas no puede ser negativo")
        
        return self.get_cost()*hours

    def get_description(self):
        return f"Reservar sala número: {self.room_number}"

    def validate(self):
        if not isinstance(self.room_number, int) or self.room_number <= 0:
            raise ValueError("El número de habitación debe ser un entero positivo")