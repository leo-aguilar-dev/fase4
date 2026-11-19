class SoftwareFJError(Exception):
    """Excepción base del sistema. Todas las excepciones personalizadas heredan de ella."""

    def __init__(self, message, code="ERROR_GENERAL"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"[{self.code}] {self.message}"


class InvalidDataError(SoftwareFJError):
    """Se lanza cuando un dato tiene un formato o valor inválido."""

    def __init__(self, message):
        super().__init__(message, "DATO_INVALIDO")


class MissingParameterError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio."""

    def __init__(self, parameter_name):
        super().__init__(f"Falta el parámetro obligatorio: '{parameter_name}'", "PARAMETRO_FALTANTE")
        self.parameter_name = parameter_name


class OperationNotAllowedError(SoftwareFJError):
    """Se lanza cuando se intenta una operación no permitida en el estado actual."""

    def __init__(self, message):
        super().__init__(message, "OPERACION_NO_PERMITIDA")


class ReservationError(SoftwareFJError):
    """Se lanza cuando un intento de reserva es incorrecto."""

    def __init__(self, message):
        super().__init__(message, "ERROR_RESERVA")


class ServiceUnavailableError(SoftwareFJError):
    """Se lanza cuando el servicio solicitado no está disponible."""

    def __init__(self, service_name):
        super().__init__(f"El servicio '{service_name}' no está disponible", "SERVICIO_NO_DISPONIBLE")
        self.service_name = service_name


class CalculationError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos es inconsistente."""

    def __init__(self, message):
        super().__init__(message, "CALCULO_INCONSISTENTE")
