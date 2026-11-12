from service import Service

class SpecializedConsulting(Service):
    def __init__(self, name, cost, consultant_name):
        super().__init__(name, cost)
        self.consultant_name = consultant_name

    def calculate_cost(self, hours):
        if hours < 0:
            raise ValueError("El número de horas no puede ser negativo")
        
        return self.get_cost() * hours

    def get_description(self):
        return f"Consultoría especializada con {self.consultant_name}"

    def validate(self):
        if not isinstance(self.consultant_name, str) or not self.consultant_name:
            raise ValueError("El nombre del consultor debe ser una cadena no vacía")