from models.entity import Entity
from models.exceptions import (
    CalculationError,
    InvalidDataError,
    MissingParameterError,
    OperationNotAllowedError,
    ReservationError,
    ServiceUnavailableError,
    SoftwareFJError,
)
from models.service_rent_equipment import RentEquipment
from utils.logger import get_logger, log_error

STATUS_PENDING = "PENDIENTE"
STATUS_CONFIRMED = "CONFIRMADA"
STATUS_CANCELLED = "CANCELADA"
STATUS_PROCESSED = "PROCESADA"

MAX_DURATION = 720
MAX_DISCOUNT = 0.5

logger = get_logger("reservation")


class Reservation(Entity):
    """Integra un cliente, un servicio, una duración y un estado.

    'units' solo se usa en servicios que lo requieren (por ejemplo, alquiler de equipos).
    """

    def __init__(self, entity_id, client, service, duration, units=None):
        super().__init__(entity_id)
        self.__client = client
        self.__service = service
        self.__duration = duration
        self.__units = units
        self.__status = STATUS_PENDING
        self.__total_cost = 0.0

        try:
            self.validate()
        except (MissingParameterError, InvalidDataError, SoftwareFJError) as error:
            log_error(logger, error, f"Reserva {entity_id} rechazada")
            raise ReservationError(f"No se pudo crear la reserva {entity_id}") from error
        else:
            logger.info(f"Reserva {entity_id} creada en estado {self.__status}")

    def get_client(self):
        return self.__client

    def get_service(self):
        return self.__service

    def get_duration(self):
        return self.__duration

    def get_units(self):
        return self.__units

    def get_status(self):
        return self.__status

    def get_total_cost(self):
        return self.__total_cost

    def validate(self):
        """Valida que cliente, servicio y duración existan y sean coherentes."""
        if self.get_id() is None or str(self.get_id()).strip() == "":
            raise MissingParameterError("entity_id")
        if self.__client is None:
            raise MissingParameterError("client")
        if self.__service is None:
            raise MissingParameterError("service")
        if self.__duration is None:
            raise MissingParameterError("duration")
        if isinstance(self.__duration, bool) or not isinstance(self.__duration, (int, float)):
            raise InvalidDataError("La duración debe ser un número")
        if self.__duration <= 0 or self.__duration > MAX_DURATION:
            raise InvalidDataError(f"La duración debe estar entre 1 y {MAX_DURATION}")
        if self.__units is not None and (isinstance(self.__units, bool) or not isinstance(self.__units, int) or self.__units <= 0):
            raise InvalidDataError("Las unidades deben ser un entero positivo")
        if isinstance(self.__service, RentEquipment) and self.__units is None:
            raise MissingParameterError("units")

    def get_description(self):
        service_description = self.__service.get_description()
        return (
            f"Reserva {self.get_id()} | Cliente: {self._get_client_name()} | "
            f"{service_description} | Duración: {self.__duration} | Estado: {self.__status}"
        )

    def _get_client_name(self):
        if hasattr(self.__client, "get_name"):
            return self.__client.get_name()
        return str(self.__client)

    def calculate_base_cost(self):
        """Calcula el costo usando el método polimórfico calculate_cost del servicio."""
        try:
            cost = self.__service.calculate_cost(self.__duration, self.__units)
        except (ValueError, TypeError, SoftwareFJError) as error:
            raise CalculationError(f"El servicio no pudo calcular el costo de la reserva {self.get_id()}") from error

        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
            raise CalculationError(f"Costo inconsistente obtenido: {cost}")
        return float(cost)

    def calculate_total(self, tax_rate=None, discount=None):
        """Variantes del cálculo (simula sobrecarga):
        - calculate_total()                 -> solo costo base
        - calculate_total(tax_rate)         -> costo con impuesto
        - calculate_total(tax_rate, discount) -> costo con impuesto y descuento
        - calculate_total(discount=x)       -> costo con descuento
        """
        base_cost = self.calculate_base_cost()

        if tax_rate is not None and (isinstance(tax_rate, bool) or not isinstance(tax_rate, (int, float)) or not 0 <= tax_rate <= 1):
            raise CalculationError(f"Tasa de impuesto inválida: {tax_rate}")
        if discount is not None and (isinstance(discount, bool) or not isinstance(discount, (int, float)) or not 0 <= discount <= MAX_DISCOUNT):
            raise CalculationError(f"Descuento inválido: {discount} (máximo {MAX_DISCOUNT})")

        total = base_cost
        if discount is not None:
            total -= base_cost * discount
        if tax_rate is not None:
            total += total * tax_rate
        return round(total, 2)

    def confirm(self):
        """Confirma la reserva si está pendiente y el servicio está disponible."""
        try:
            if self.__status != STATUS_PENDING:
                raise OperationNotAllowedError(
                    f"No se puede confirmar la reserva {self.get_id()} en estado {self.__status}"
                )
            try:
                if isinstance(self.__service, RentEquipment):
                    self.__service.reserve_units(self.__units)
                else:
                    self.__service.validate()
            except (ValueError, TypeError) as error:
                raise ServiceUnavailableError(self.__service.get_name()) from error
        except (OperationNotAllowedError, ServiceUnavailableError, SoftwareFJError) as error:
            log_error(logger, error, f"Confirmación fallida de reserva {self.get_id()}")
            raise
        else:
            self.__status = STATUS_CONFIRMED
            logger.info(f"Reserva {self.get_id()} confirmada")

    def cancel(self):
        """Cancela la reserva. No se permite si ya fue cancelada o procesada."""
        if self.__status in (STATUS_CANCELLED, STATUS_PROCESSED):
            error = OperationNotAllowedError(
                f"No se puede cancelar la reserva {self.get_id()} en estado {self.__status}"
            )
            log_error(logger, error)
            raise error
        
        if self.__status == STATUS_CONFIRMED and isinstance(self.__service, RentEquipment):
            self.__service.release_units(self.__units)

        self.__status = STATUS_CANCELLED
        logger.info(f"Reserva {self.get_id()} cancelada")

    def process(self, tax_rate=None, discount=None):
        """Procesa una reserva confirmada calculando su costo total."""
        logger.debug(f"Iniciando procesamiento de la reserva {self.get_id()}")
        try:
            if self.__status != STATUS_CONFIRMED:
                raise OperationNotAllowedError(
                    f"Solo se pueden procesar reservas confirmadas (actual: {self.__status})"
                )
            total = self.calculate_total(tax_rate, discount)
        except OperationNotAllowedError as error:
            log_error(logger, error, f"Procesamiento rechazado de reserva {self.get_id()}")
            raise
        except CalculationError as error:
            log_error(logger, error, f"Error de cálculo en reserva {self.get_id()}")
            raise ReservationError(f"La reserva {self.get_id()} no pudo procesarse") from error
        else:
            self.__total_cost = total
            self.__status = STATUS_PROCESSED
            logger.info(f"Reserva {self.get_id()} procesada. Total: ${total:,.2f}")
            return total
        finally:
            logger.debug(f"Fin del intento de procesamiento de la reserva {self.get_id()} (estado: {self.__status})")

    def __str__(self):
        return self.get_description()
