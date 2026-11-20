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
from models.reservation import Reservation
from models.service_rent_equipment import RentEquipment
from models.service_reserve_room import ReserveRoom
from models.service_specialized_consulting import SpecializedConsulting
from utils.logger import get_logger, log_error

logger = get_logger("simulation")

IVA_ESTANDAR = 0.19
DESCUENTO_CORPORATIVO = 0.15
MINIMO_OPERACIONES = 10

try:
    from models.client import Client
except ImportError:

    class Client(Entity):
        """Clase que representa un cliente de Software FJ con encapsulación y validaciones."""

        def __init__(self, entity_id, name, email, phone):
            super().__init__(entity_id)
            self.__name = name
            self.__email = email
            self.__phone = phone
            self.validate()

        def get_name(self):
            return self.__name

        def get_email(self):
            return self.__email

        def get_phone(self):
            return self.__phone

        def validate(self):
            if not isinstance(self.__name, str) or self.__name.strip() == "":
                raise MissingParameterError("name")
            if not isinstance(self.__email, str) or "@" not in self.__email:
                raise InvalidDataError(f"Correo electrónico inválido: '{self.__email}'")
            if not isinstance(self.__phone, str) or len(self.__phone.strip()) < 7:
                raise InvalidDataError(f"Número telefónico inválido: '{self.__phone}'")

        def get_description(self):
            return f"Cliente [{self.get_id()}]: {self.__name} ({self.__email})"


def ejecutar_simulacion():
    """Ejecuta 12 operaciones completas para validar la estabilidad y manejo de errores."""
    clientes_registrados = []
    servicios_disponibles = []
    reservas_sistema = []
    operaciones_ejecutadas = 0

    logger.info("=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")

    # -------------------------------------------------------------------------
    # OPERACIÓN 1: Registro válido de un cliente corporativo
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cliente_1 = Client("CLI-001", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo en Operación 1")
    else:
        clientes_registrados.append(cliente_1)
        logger.info(f"Operación 1 exitosa: {cliente_1.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Registro válido de un segundo cliente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cliente_2 = Client("CLI-002", "Carlos Mendoza", "cmendoza@techcol.co", "3209876543")
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo en Operación 2")
    else:
        clientes_registrados.append(cliente_2)
        logger.info(f"Operación 2 exitosa: {cliente_2.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 3: Registro inválido de cliente (correo sin '@' y teléfono corto)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cliente_invalido = Client("CLI-003", "Pedro Pérez", "correo_sin_arroba.com", "123")
        clientes_registrados.append(cliente_invalido)
    except (InvalidDataError, MissingParameterError) as error:
        log_error(logger, error, "Operación 3 controlada (registro de cliente inválido)")
    finally:
        logger.debug("Operación 3 finalizada: verificación de validación de cliente completada.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Creación correcta de los 3 tipos de servicios especializados
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        sala_juntas = ReserveRoom("SRV-001", "Sala Ejecutiva A", 80000.0, 101)
        equipos_portatiles = RentEquipment("SRV-002", "Portátil Dell Precision", 45000.0, 5)
        asesoria_arquitectura = SpecializedConsulting("SRV-003", "Asesoría Cloud", 150000.0, "Ing. Héctor Aguilar")
        sala_juntas.validate()
        equipos_portatiles.validate(1)
        asesoria_arquitectura.validate()
    except (ValueError, SoftwareFJError) as error:
        log_error(logger, error, "Fallo en Operación 4")
    else:
        servicios_disponibles.extend([sala_juntas, equipos_portatiles, asesoria_arquitectura])
        logger.info(f"Operación 4 exitosa: {len(servicios_disponibles)} servicios creados y validados.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 5: Creación y modificación incorrecta de un servicio (costo negativo)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        sala_defectuosa = ReserveRoom("SRV-004", "Sala Fantasma", 50000.0, 0)
        sala_defectuosa.set_cost(-25000.0)
    except ValueError as error:
        try:
            raise InvalidDataError("Parámetros de costo o habitación inválidos al configurar servicio") from error
        except InvalidDataError as custom_error:
            log_error(logger, custom_error, "Operación 5 controlada (servicio inválido)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa de Sala (con impuesto y descuento aplicados)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_1 = Reservation("RES-001", clientes_registrados[0], servicios_disponibles[0], 4)
        reserva_1.confirm()
        total_r1 = reserva_1.process(tax_rate=IVA_ESTANDAR, discount=DESCUENTO_CORPORATIVO)
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo en Operación 6")
    else:
        reservas_sistema.append(reserva_1)
        logger.info(f"Operación 6 exitosa: {reserva_1.get_description()} | Total: ${total_r1:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 7: Reserva exitosa de Alquiler de Equipos (solo con impuesto)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_2 = Reservation("RES-002", clientes_registrados[1], servicios_disponibles[1], 2, units=3)
        reserva_2.confirm()
        total_r2 = reserva_2.process(tax_rate=IVA_ESTANDAR)
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo en Operación 7")
    else:
        reservas_sistema.append(reserva_2)
        logger.info(f"Operación 7 exitosa: {reserva_2.get_description()} | Total: ${total_r2:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 8: Reserva exitosa de Asesoría Especializada (costo base sin extras)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_3 = Reservation("RES-003", clientes_registrados[0], servicios_disponibles[2], 3)
        reserva_3.confirm()
        total_r3 = reserva_3.process()
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo en Operación 8")
    else:
        reservas_sistema.append(reserva_3)
        logger.info(f"Operación 8 exitosa: {reserva_3.get_description()} | Total: ${total_r3:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 9: Intento fallido de crear reserva con duración inválida (negativa)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_invalida = Reservation("RES-004", clientes_registrados[0], servicios_disponibles[0], -5)
        reservas_sistema.append(reserva_invalida)
    except ReservationError as error:
        log_error(logger, error, "Operación 9 controlada (creación de reserva inválida)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Reserva fallida por servicio no disponible (stock insuficiente)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_sin_stock = Reservation("RES-005", clientes_registrados[1], servicios_disponibles[1], 3, units=20)
        reserva_sin_stock.confirm()
    except ServiceUnavailableError as error:
        log_error(logger, error, "Operación 10 controlada (stock insuficiente al confirmar)")
    finally:
        logger.debug("Operación 10 finalizada: control de disponibilidad verificado.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 11: Operación no permitida (procesar sin confirmar y cancelar procesada)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_pendiente = Reservation("RES-006", clientes_registrados[1], servicios_disponibles[2], 2)
        reserva_pendiente.process()
    except OperationNotAllowedError as error:
        log_error(logger, error, "Operación 11a controlada (procesamiento sin confirmación)")

    try:
        reservas_sistema[0].cancel()
    except OperationNotAllowedError as error:
        log_error(logger, error, "Operación 11b controlada (cancelación de reserva ya procesada)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Cancelación válida de reserva y prueba de cálculo inconsistente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        reserva_cancelable = Reservation("RES-007", clientes_registrados[0], servicios_disponibles[0], 2)
        reserva_cancelable.confirm()
        try:
            reserva_cancelable.calculate_total(discount=0.90)
        except CalculationError as calc_error:
            log_error(logger, calc_error, "Operación 12a controlada (descuento fuera de rango)")
        reserva_cancelable.cancel()
    except SoftwareFJError as error:
        log_error(logger, error, "Fallo inesperado en Operación 12")
    else:
        reservas_sistema.append(reserva_cancelable)
        logger.info(f"Operación 12b exitosa: {reserva_cancelable.get_description()}")

    # -------------------------------------------------------------------------
    # RESUMEN FINAL EN CONSOLA Y LOGS
    # -------------------------------------------------------------------------
    logger.info("=== RESUMEN DE LA SIMULACIÓN ===")
    logger.info(f"Total operaciones ejecutadas: {operaciones_ejecutadas} (Mínimo requerido: {MINIMO_OPERACIONES})")
    logger.info(f"Clientes activos en memoria: {len(clientes_registrados)}")
    logger.info(f"Servicios activos en memoria: {len(servicios_disponibles)}")
    logger.info(f"Reservas registradas en memoria: {len(reservas_sistema)}")
    logger.info("=== FIN DE SIMULACIÓN SIN INTERRUPCIONES ===")