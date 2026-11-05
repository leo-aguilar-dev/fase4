from service import Service

class RentEquipment(Service):
    def __init__(self, name, cost, stock):
        super().__init__(name, cost)
        self.stock = stock

    def calculate_cost(self, days, units):
        if days < 0:
            raise ValueError("El número de días no puede ser negativo")
        
        if units < 0:
            raise ValueError("El número de unidades no puede ser negativo")
        
        return self.get_cost() * days * units

    def get_description(self):
        return f"Alquilar equipo: {self.get_name()} (Stock disponible: {self.stock})"

    def validate(self, units):
        if units <= 0:
            raise ValueError("El número de unidades no puede ser cero o negativo")
        
        if units > self.stock:
            raise ValueError("No hay suficiente stock disponible para alquilar")