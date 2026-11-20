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

IVA_ESTANDAR = 0.19
DESCUENTO_CORPORATIVO = 0.15
MINIMO_OPERACIONES = 10


def _registrar_fallo_sin_detener(error, contexto):
    """Registra cualquier error (controlado o inesperado) en los logs sin interrumpir la simulación."""
    if isinstance(error, SoftwareFJError):
        log_error(logger, error, contexto)
    else:
        error_envuelto = ReservationError(f"Error inesperado ({type(error).__name__}): {error}")
        error_envuelto.__cause__ = error
        log_error(logger, error_envuelto, contexto)


def _agregar_sin_duplicar(coleccion, entidad, tipo_entidad):
    """Agrega una entidad a la lista compartida si su ID aún no está registrado."""
    if any(item.get_id() == entidad.get_id() for item in coleccion):
        logger.info(f"{tipo_entidad} con ID '{entidad.get_id()}' ya existe en el sistema; se reutiliza.")
        for item in coleccion:
            if item.get_id() == entidad.get_id():
                return item
    coleccion.append(entidad)
    return entidad


def ejecutar_simulacion(clientes=None, servicios=None, reservas=None):
    """Ejecuta 12 operaciones integrando los datos con las listas del sistema."""
    clientes_registrados = clientes if clientes is not None else []
    servicios_disponibles = servicios if servicios is not None else []
    reservas_sistema = reservas if reservas is not None else []
    operaciones_ejecutadas = 0

    logger.info("=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")

    # -------------------------------------------------------------------------
    # OPERACIÓN 1: Registro válido de un cliente corporativo
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    cliente_1 = None
    try:
        candidato_1 = Client("CLI-001", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
        cliente_1 = _agregar_sin_duplicar(clientes_registrados, candidato_1, "Cliente")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 1")
    else:
        logger.info(f"Operación 1 exitosa: {cliente_1.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Registro válido de un segundo cliente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    cliente_2 = None
    try:
        candidato_2 = Client("CLI-002", "Carlos Mendoza", "cmendoza@techcol.co", "3209876543")
        cliente_2 = _agregar_sin_duplicar(clientes_registrados, candidato_2, "Cliente")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 2")
    else:
        logger.info(f"Operación 2 exitosa: {cliente_2.get_description()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 3: Registro inválido de cliente (correo sin '@' y teléfono corto)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cliente_invalido = Client("CLI-003", "Pedro Pérez", "correo_sin_arroba.com", "123")
        _agregar_sin_duplicar(clientes_registrados, cliente_invalido, "Cliente")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 3 controlada (registro de cliente inválido)")
    finally:
        logger.debug("Operación 3 finalizada.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Creación correcta de los 3 tipos de servicios especializados
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    sala_juntas = None
    equipos_portatiles = None
    asesoria_arquitectura = None
    try:
        srv_1 = ReserveRoom("SRV-001", "Sala Ejecutiva A", 80000.0, 101)
        srv_2 = RentEquipment("SRV-002", "Portátil Dell Precision", 45000.0, 5)
        srv_3 = SpecializedConsulting("SRV-003", "Asesoría Cloud", 150000.0, "Ing. Héctor Aguilar")

        srv_1.validate()
        srv_2.validate(1)
        srv_3.validate()

        sala_juntas = _agregar_sin_duplicar(servicios_disponibles, srv_1, "Servicio")
        equipos_portatiles = _agregar_sin_duplicar(servicios_disponibles, srv_2, "Servicio")
        asesoria_arquitectura = _agregar_sin_duplicar(servicios_disponibles, srv_3, "Servicio")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 4")
    else:
        logger.info(f"Operación 4 exitosa: {len(servicios_disponibles)} servicios disponibles en el sistema.")

    # -------------------------------------------------------------------------
    # OPERACIÓN 5: Creación y modificación incorrecta de un servicio (costo negativo)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        sala_defectuosa = ReserveRoom("SRV-004", "Sala Fantasma", 50000.0, 0)
        sala_defectuosa.set_cost(-25000.0)
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 5 controlada (servicio inválido)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa de Sala (con impuesto y descuento aplicados)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    reserva_1 = None
    try:
        cli_ref = cliente_1 or (clientes_registrados[0] if clientes_registrados else None)
        srv_ref = sala_juntas or (servicios_disponibles[0] if servicios_disponibles else None)
        res_1 = Reservation("RES-001", cli_ref, srv_ref, 4)
        res_1.confirm()
        total_r1 = res_1.process(tax_rate=IVA_ESTANDAR, discount=DESCUENTO_CORPORATIVO)
        reserva_1 = _agregar_sin_duplicar(reservas_sistema, res_1, "Reserva")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 6")
    else:
        logger.info(f"Operación 6 exitosa: {reserva_1.get_description()} | Total: ${total_r1:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 7: Reserva exitosa de Alquiler de Equipos (solo con impuesto)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = cliente_2 or (clientes_registrados[-1] if clientes_registrados else None)
        srv_ref = equipos_portatiles
        res_2 = Reservation("RES-002", cli_ref, srv_ref, 2, units=3)
        res_2.confirm()
        total_r2 = res_2.process(tax_rate=IVA_ESTANDAR)
        reserva_2 = _agregar_sin_duplicar(reservas_sistema, res_2, "Reserva")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 7")
    else:
        logger.info(f"Operación 7 exitosa: {reserva_2.get_description()} | Total: ${total_r2:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 8: Reserva exitosa de Asesoría Especializada (costo base sin extras)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = cliente_1 or (clientes_registrados[0] if clientes_registrados else None)
        srv_ref = asesoria_arquitectura
        res_3 = Reservation("RES-003", cli_ref, srv_ref, 3)
        res_3.confirm()
        total_r3 = res_3.process()
        reserva_3 = _agregar_sin_duplicar(reservas_sistema, res_3, "Reserva")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 8")
    else:
        logger.info(f"Operación 8 exitosa: {reserva_3.get_description()} | Total: ${total_r3:,.2f}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 9: Intento fallido de crear reserva con duración inválida (negativa)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = clientes_registrados[0] if clientes_registrados else None
        srv_ref = servicios_disponibles[0] if servicios_disponibles else None
        res_inv = Reservation("RES-004", cli_ref, srv_ref, -5)
        _agregar_sin_duplicar(reservas_sistema, res_inv, "Reserva")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 9 controlada (creación de reserva inválida)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Reserva fallida por servicio no disponible (stock insuficiente)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = clientes_registrados[-1] if clientes_registrados else None
        srv_ref = equipos_portatiles
        res_sin_stock = Reservation("RES-005", cli_ref, srv_ref, 3, units=20)
        res_sin_stock.confirm()
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 10 controlada (stock insuficiente al confirmar)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 11: Operación no permitida (procesar sin confirmar y cancelar procesada)
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = clientes_registrados[-1] if clientes_registrados else None
        srv_ref = asesoria_arquitectura
        res_pend = Reservation("RES-006", cli_ref, srv_ref, 2)
        res_pend.process()
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 11a controlada (procesamiento sin confirmación)")

    try:
        if reserva_1 is not None:
            reserva_1.cancel()
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Operación 11b controlada (cancelación de reserva ya procesada)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Cancelación válida de reserva y prueba de cálculo inconsistente
    # -------------------------------------------------------------------------
    operaciones_ejecutadas += 1
    try:
        cli_ref = clientes_registrados[0] if clientes_registrados else None
        srv_ref = servicios_disponibles[0] if servicios_disponibles else None
        res_canc = Reservation("RES-007", cli_ref, srv_ref, 2)
        res_canc.confirm()
        try:
            res_canc.calculate_total(discount=0.90)
        except Exception as calc_error:
            _registrar_fallo_sin_detener(calc_error, "Operación 12a controlada (descuento fuera de rango)")
        res_canc.cancel()
        reserva_12 = _agregar_sin_duplicar(reservas_sistema, res_canc, "Reserva")
    except Exception as error:
        _registrar_fallo_sin_detener(error, "Fallo en Operación 12")
    else:
        logger.info(f"Operación 12b exitosa: {reserva_12.get_description()}")

    # -------------------------------------------------------------------------
    # RESUMEN FINAL EN CONSOLA Y LOGS
    # -------------------------------------------------------------------------
    logger.info("=== RESUMEN DE LA SIMULACIÓN ===")
    logger.info(f"Total operaciones ejecutadas: {operaciones_ejecutadas} (Mínimo requerido: {MINIMO_OPERACIONES})")
    logger.info(f"Clientes totales en el sistema: {len(clientes_registrados)}")
    logger.info(f"Servicios totales en el sistema: {len(servicios_disponibles)}")
    logger.info(f"Reservas totales en el sistema: {len(reservas_sistema)}")
    logger.info("=== FIN DE SIMULACIÓN SIN INTERRUPCIONES ===")

    return clientes_registrados, servicios_disponibles, reservas_sistema