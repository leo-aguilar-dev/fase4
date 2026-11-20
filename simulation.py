from models.client import Client
from models.exceptions import (
    ReservationError,
    SoftwareFJError,
)
from models.reservation import Reservation
from models.service_rent_equipment import RentEquipment
from models.service_reserve_room import ReserveRoom
from models.service_specialized_consulting import SpecializedConsulting
from utils.logger import get_logger, log_error

logger = get_logger("simulation")

STANDARD_TAX = 0.19
CORPORATE_DISCOUNT = 0.15
MIN_OPERATIONS = 10


def _log_failure_without_stopping(error, context):
    """Registra cualquier error (controlado o inesperado) en los logs sin interrumpir la simulación."""
    if isinstance(error, SoftwareFJError):
        log_error(logger, error, context)
    else:
        wrapped_error = ReservationError(f"Error inesperado ({type(error).__name__}): {error}")
        wrapped_error.__cause__ = error
        log_error(logger, wrapped_error, context)


def _add_without_duplicates(collection, entity, entity_type):
    """Agrega una entidad a la lista compartida si su ID aún no está registrado."""
    if any(item.get_id() == entity.get_id() for item in collection):
        logger.info(f"{entity_type} con ID '{entity.get_id()}' ya existe en el sistema; se reutiliza.")
        for item in collection:
            if item.get_id() == entity.get_id():
                return item
    collection.append(entity)
    return entity


def run_simulation(clients=None, services=None, reservations=None):
    """Ejecuta 12 operaciones integrando los datos con las listas del sistema."""
    registered_clients = clients if clients is not None else []
    available_services = services if services is not None else []
    system_reservations = reservations if reservations is not None else []
    executed_operations = 0

    logger.info("=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")

    # -------------------------------------------------------------------------
    # OPERACIÓN 1: Registro válido de un cliente corporativo
    # -------------------------------------------------------------------------
    executed_operations += 1
    client_1 = None
    try:
        candidate_1 = Client("CLI-001", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
        client_1 = _add_without_duplicates(registered_clients, candidate_1, "Cliente")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 1")
    else:
        logger.info(f"Operación 1 exitosa: {client_1.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Registro válido de un segundo cliente
    # -------------------------------------------------------------------------
    executed_operations += 1
    client_2 = None
    try:
        candidate_2 = Client("CLI-002", "Carlos Mendoza", "cmendoza@techcol.co", "3209876543")
        client_2 = _add_without_duplicates(registered_clients, candidate_2, "Cliente")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 2")
    else:
        logger.info(f"Operación 2 exitosa: {client_2.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 3: Registro inválido de cliente (correo sin '@' y teléfono corto)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        invalid_client = Client("CLI-003", "Pedro Pérez", "correo_sin_arroba.com", "123")
        _add_without_duplicates(registered_clients, invalid_client, "Cliente")
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 3 controlada (registro de cliente inválido)")
    finally:
        logger.debug("Operación 3 finalizada.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Creación correcta de los 3 tipos de servicios especializados
    # -------------------------------------------------------------------------
    executed_operations += 1
    meeting_room = None
    laptops = None
    architecture_consulting = None
    try:
        srv_1 = ReserveRoom("SRV-001", "Sala Ejecutiva A", 80000.0, 101)
        srv_2 = RentEquipment("SRV-002", "Portátil Dell Precision", 45000.0, 5)
        srv_3 = SpecializedConsulting("SRV-003", "Asesoría Cloud", 150000.0, "Ing. Héctor Aguilar")

        srv_1.validate()
        srv_2.validate(1)
        srv_3.validate()

        meeting_room = _add_without_duplicates(available_services, srv_1, "Servicio")
        laptops = _add_without_duplicates(available_services, srv_2, "Servicio")
        architecture_consulting = _add_without_duplicates(available_services, srv_3, "Servicio")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 4")
    else:
        logger.info(f"Operación 4 exitosa: {len(available_services)} servicios disponibles en el sistema.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 5: Creación y modificación incorrecta de un servicio (costo negativo)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        faulty_room = ReserveRoom("SRV-004", "Sala Fantasma", 50000.0, 0)
        faulty_room.set_cost(-25000.0)
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 5 controlada (servicio inválido)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa de Sala (con impuesto y descuento aplicados)
    # -------------------------------------------------------------------------
    executed_operations += 1
    reservation_1 = None
    try:
        cli_ref = client_1 or (registered_clients[0] if registered_clients else None)
        srv_ref = meeting_room or (available_services[0] if available_services else None)
        res_1 = Reservation("RES-001", cli_ref, srv_ref, 4)
        res_1.confirm()
        total_r1 = res_1.process(tax_rate=STANDARD_TAX, discount=CORPORATE_DISCOUNT)
        reservation_1 = _add_without_duplicates(system_reservations, res_1, "Reserva")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 6")
    else:
        logger.info(f"Operación 6 exitosa: {reservation_1.get_description()} | Total: ${total_r1:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 7: Reserva exitosa de Alquiler de Equipos (solo con impuesto)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = client_2 or (registered_clients[-1] if registered_clients else None)
        srv_ref = laptops
        res_2 = Reservation("RES-002", cli_ref, srv_ref, 2, units=3)
        res_2.confirm()
        total_r2 = res_2.process(tax_rate=STANDARD_TAX)
        reservation_2 = _add_without_duplicates(system_reservations, res_2, "Reserva")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 7")
    else:
        logger.info(f"Operación 7 exitosa: {reservation_2.get_description()} | Total: ${total_r2:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 8: Reserva exitosa de Asesoría Especializada (costo base sin extras)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = client_1 or (registered_clients[0] if registered_clients else None)
        srv_ref = architecture_consulting
        res_3 = Reservation("RES-003", cli_ref, srv_ref, 3)
        res_3.confirm()
        total_r3 = res_3.process()
        reservation_3 = _add_without_duplicates(system_reservations, res_3, "Reserva")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 8")
    else:
        logger.info(f"Operación 8 exitosa: {reservation_3.get_description()} | Total: ${total_r3:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 9: Intento fallido de crear reserva con duración inválida (negativa)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = registered_clients[0] if registered_clients else None
        srv_ref = available_services[0] if available_services else None
        invalid_res = Reservation("RES-004", cli_ref, srv_ref, -5)
        _add_without_duplicates(system_reservations, invalid_res, "Reserva")
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 9 controlada (creación de reserva inválida)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Reserva fallida por servicio no disponible (stock insuficiente)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = registered_clients[-1] if registered_clients else None
        srv_ref = laptops
        out_of_stock_res = Reservation("RES-005", cli_ref, srv_ref, 3, units=20)
        out_of_stock_res.confirm()
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 10 controlada (stock insuficiente al confirmar)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 11: Operación no permitida (procesar sin confirmar y cancelar procesada)
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = registered_clients[-1] if registered_clients else None
        srv_ref = architecture_consulting
        pending_res = Reservation("RES-006", cli_ref, srv_ref, 2)
        pending_res.process()
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 11a controlada (procesamiento sin confirmación)")

    try:
        if reservation_1 is not None:
            reservation_1.cancel()
    except Exception as error:
        _log_failure_without_stopping(error, "Operación 11b controlada (cancelación de reserva ya procesada)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Cancelación válida de reserva y prueba de cálculo inconsistente
    # -------------------------------------------------------------------------
    executed_operations += 1
    try:
        cli_ref = registered_clients[0] if registered_clients else None
        srv_ref = available_services[0] if available_services else None
        cancellable_res = Reservation("RES-007", cli_ref, srv_ref, 2)
        cancellable_res.confirm()
        try:
            cancellable_res.calculate_total(discount=0.90)
        except Exception as calc_error:
            _log_failure_without_stopping(calc_error, "Operación 12a controlada (descuento fuera de rango)")
        cancellable_res.cancel()
        reservation_12 = _add_without_duplicates(system_reservations, cancellable_res, "Reserva")
    except Exception as error:
        _log_failure_without_stopping(error, "Fallo en Operación 12")
    else:
        logger.info(f"Operación 12b exitosa: {reservation_12.get_description()}")

    # -------------------------------------------------------------------------
    # RESUMEN FINAL EN CONSOLA Y LOGS
    # -------------------------------------------------------------------------
    logger.info("=== RESUMEN DE LA SIMULACIÓN ===")
    logger.info(f"Total operaciones ejecutadas: {executed_operations} (Mínimo requerido: {MIN_OPERATIONS})")
    logger.info(f"Clientes totales en el sistema: {len(registered_clients)}")
    logger.info(f"Servicios totales en el sistema: {len(available_services)}")
    logger.info(f"Reservas totales en el sistema: {len(system_reservations)}")
    logger.info("=== FIN DE SIMULACIÓN SIN INTERRUPCIONES ===")

    return registered_clients, available_services, system_reservations


if __name__ == "__main__":
    run_simulation()