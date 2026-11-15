import os
import sys

# Agrega la carpeta 'models' al path de Python para evitar errores de importación
# en los módulos de servicios que usan 'from service import Service'
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RUTA_BASE, "models"))

# Importación de las clases del sistema y utilidades de registro (logs)
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

# Inicializa el logger específico para el módulo de simulación
logger = get_logger("simulation")

# Constantes de configuración para la simulación de Software FJ
IVA_ESTANDAR = 0.19
DESCUENTO_CORPORATIVO = 0.15
MINIMO_OPERACIONES = 10

# Intenta importar la clase Client del Punto 1; si aún no está en el repositorio,
# define una implementación compatible que hereda de Entity para ejecutar las pruebas
try:
    from models.client import Client
except ImportError:

    class Client(Entity):
        """Clase que representa un cliente de Software FJ con encapsulación y validaciones."""

        def __init__(self, entity_id, name, email, phone):
            # Llama al constructor de la clase abstracta padre Entity
            super().__init__(entity_id)
            # Atributos privados encapsulados
            self.__name = name
            self.__email = email
            self.__phone = phone
            # Valida los datos inmediatamente al instanciar el objeto
            self.validate()

        def get_name(self):
            # Retorna el nombre del cliente
            return self.__name

        def get_email(self):
            # Retorna el correo electrónico del cliente
            return self.__email

        def get_phone(self):
            # Retorna el teléfono del cliente
            return self.__phone

        def validate(self):
            # Verifica que los campos obligatorios no estén vacíos ni sean nulos
            if self.get_id() is None or str(self.get_id()).strip() == "":
                raise MissingParameterError("entity_id")
            if not isinstance(self.__name, str) or self.__name.strip() == "":
                raise MissingParameterError("name")
            if not isinstance(self.__email, str) or "@" not in self.__email:
                raise InvalidDataError(f"Correo electrónico inválido: '{self.__email}'")
            if not isinstance(self.__phone, str) or len(self.__phone.strip()) < 7:
                raise InvalidDataError(f"Número telefónico inválido: '{self.__phone}'")

        def get_description(self):
            # Devuelve una cadena descriptiva con los datos del cliente
            return f"Cliente [{self.get_id()}]: {self.__name} ({self.__email})"


def ejecutar_simulacion():
    """Ejecuta 12 operaciones completas para validar la estabilidad y manejo de errores."""
    # Listas en memoria para almacenar objetos sin utilizar bases de datos
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
        # Se instancia un cliente con todos sus datos válidos
        cliente_1 = Client("CLI-001", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
    except SoftwareFJError as error:
        # Registra cualquier fallo inesperado en el archivo de logs
        log_error(logger, error, "Fallo en Operación 1")
    else:
        # Si no hubo excepciones, se añade a la lista en memoria y se registra el éxito
        clientes_registrados.append(cliente_1)
        logger.info(f"Operación 1 exitosa: {cliente_1.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Registro válido de un segundo cliente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        # Se crea un segundo cliente válido para posteriores reservas
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
        # Intento deliberado de crear un cliente con correo mal formado
        cliente_invalido = Client("CLI-003", "Pedro Pérez", "correo_sin_arroba.com", "123")
        clientes_registrados.append(cliente_invalido)
    except (InvalidDataError, MissingParameterError) as error:
        # Captura la excepción personalizada sin detener la ejecución del programa
        log_error(logger, error, "Operación 3 controlada (registro de cliente inválido)")
    finally:
        # El bloque finally siempre se ejecuta para dejar trazabilidad del intento
        logger.debug("Operación 3 finalizada: verificación de validación de cliente completada.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Creación correcta de los 3 tipos de servicios especializados
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        # Instancia de los tres servicios que heredan de la clase abstracta Service
        sala_juntas = ReserveRoom("Sala Ejecutiva A", 80000.0, 101)
        equipos_portatiles = RentEquipment("Portátil Dell Precision", 45000.0, 5)
        asesoria_arquitectura = SpecializedConsulting("Asesoría Cloud", 150000.0, "Ing. Héctor Aguilar")

        # Valida cada servicio antes de incorporarlo al catálogo en memoria
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
        # Se crea una sala con número de habitación inválido (0) y se intenta asignar costo negativo
        sala_defectuosa = ReserveRoom("Sala Fantasma", 50000.0, 0)
        sala_defectuosa.set_cost(-25000.0)
    except ValueError as error:
        # Encadena el ValueError nativo dentro de una excepción personalizada InvalidDataError
        try:
            raise InvalidDataError("Parámetros de costo o habitación inválidos al configurar servicio") from error
        except InvalidDataError as custom_error:
            log_error(logger, custom_error, "Operación 5 controlada (servicio inválido)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa de Sala (con impuesto y descuento aplicados)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        # Crea la reserva de sala por 4 horas para cliente_1
        reserva_1 = Reservation("RES-001", clientes_registrados[0], servicios_disponibles[0], 4)
        # Confirma la disponibilidad de la reserva
        reserva_1.confirm()
        # Procesa la reserva aplicando sobrecarga de cálculo con IVA y descuento
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
        # Crea la reserva de 3 portátiles por 2 días para cliente_2
        reserva_2 = Reservation("RES-002", clientes_registrados[1], servicios_disponibles[1], 2, units=3)
        reserva_2.confirm()
        # Procesa pasando únicamente la tasa de impuesto (variante sobrecargada)
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
        # Crea una reserva de asesoría por 3 horas para cliente_1
        reserva_3 = Reservation("RES-003", clientes_registrados[0], servicios_disponibles[2], 3)
        reserva_3.confirm()
        # Procesa sin impuestos ni descuentos (variante base de calculate_total)
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
        # Duración -5 dispara InvalidDataError encadenado en ReservationError
        reserva_invalida = Reservation("RES-004", clientes_registrados[0], servicios_disponibles[0], -5)
        reservas_sistema.append(reserva_invalida)
    except ReservationError as error:
        log_error(logger, error, "Operación 9 controlada (creación de reserva inválida)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Reserva fallida por servicio no disponible (stock insuficiente)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        # Se solicitan 20 equipos cuando el stock disponible es de solo 5 unidades
        reserva_sin_stock = Reservation("RES-005", clientes_registrados[1], servicios_disponibles[1], 3, units=20)
        # Al confirmar se valida el stock y se lanza ServiceUnavailableError encadenado
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
        # Crea una reserva válida pero intenta procesarla sin haberla confirmado antes
        reserva_pendiente = Reservation("RES-006", clientes_registrados[1], servicios_disponibles[2], 2)
        reserva_pendiente.process()
    except OperationNotAllowedError as error:
        log_error(logger, error, "Operación 11a controlada (procesamiento sin confirmación)")

    try:
        # Intenta cancelar la reserva_1 que ya fue procesada en la Operación 6
        reservas_sistema[0].cancel()
    except OperationNotAllowedError as error:
        log_error(logger, error, "Operación 11b controlada (cancelación de reserva ya procesada)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Cancelación válida de reserva y prueba de cálculo inconsistente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        # Crea una reserva, la confirma, intenta calcular un descuento ilegal (90%) y luego la cancela
        reserva_cancelable = Reservation("RES-007", clientes_registrados[0], servicios_disponibles[0], 2)
        reserva_cancelable.confirm()
        try:
            # Descuento de 0.90 supera MAX_DISCOUNT (0.50) y lanza CalculationError
            reserva_cancelable.calculate_total(discount=0.90)
        except CalculationError as calc_error:
            log_error(logger, calc_error, "Operación 12a controlada (descuento fuera de rango)")
        # Cancela correctamente la reserva confirmada
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


# Punto de entrada principal cuando se ejecuta el archivo directamente
if __name__ == "__main__":
    ejecutar_simulacion()