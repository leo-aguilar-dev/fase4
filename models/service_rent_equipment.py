from models.exceptions import InvalidDataError, MissingParameterError, ServiceUnavailableError
from models.service import Service


class RentEquipment(Service):
    def __init__(self, entity_id, name, cost, stock):
        super().__init__(entity_id, name, cost)
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise InvalidDataError("El stock inicial debe ser un entero mayor o igual a 0")
        self.stock = stock
        self.validate()

    def calculate_cost(self, duration, units=None):
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration <= 0:
            raise InvalidDataError("El número de días debe ser un número positivo")
        if units is None:
            raise MissingParameterError("units")
        if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
            raise InvalidDataError("El número de unidades debe ser un entero positivo")
        return round(self.get_cost() * duration * units, 2)

    def get_description(self):
        return f"Alquilar equipo: {self.get_name()} (Stock disponible: {self.stock})"

    def validate(self, units=None):
        if self.stock <= 0:
            raise ServiceUnavailableError(self.get_name())
        if units is not None:
            if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
                raise InvalidDataError("El número de unidades debe ser un entero positivo")
            if units > self.stock:
                raise ServiceUnavailableError(self.get_name())

    def reserve_units(self, units):
        self.validate(units)
        self.stock -= units

    def release_units(self, units):
        if units is not None and units > 0:
            self.stock += units