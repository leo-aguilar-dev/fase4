import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from models.client import Client
from models.exceptions import SoftwareFJError
from models.reservation import Reservation
from models.service_rent_equipment import RentEquipment
from models.service_reserve_room import ReserveRoom
from models.service_specialized_consulting import SpecializedConsulting
from simulacion import ejecutar_simulacion
from utils.logger import LOG_FILE, get_logger, log_error

logger = get_logger("gui")


class SoftwareFJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión Orientado a Objetos")
        self.root.geometry("980x680")
        self.root.minsize(900, 620)

        self.clientes = []
        self.servicios = []
        self.reservas = []

        self._construir_interfaz()
        self._refrescar_todo()

    def _construir_interfaz(self):
        header = tk.Frame(self.root, bg="#1f2d3d", height=55)
        header.pack(fill="x")
        tk.Label(
            header,
            text="SOFTWARE FJ — Gestión de Clientes, Servicios y Reservas",
            font=("Segoe UI", 14, "bold"),
            bg="#1f2d3d",
            fg="white",
        ).pack(pady=12)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_servicios = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)
        self.tab_simulacion_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text="1. Clientes")
        self.notebook.add(self.tab_servicios, text="2. Servicios")
        self.notebook.add(self.tab_reservas, text="3. Reservas")
        self.notebook.add(self.tab_simulacion_logs, text="4. Simulación y Logs")

        self._setup_tab_clientes()
        self._setup_tab_servicios()
        self._setup_tab_reservas()
        self._setup_tab_simulacion_logs()

    # =========================================================================
    # PESTAÑA 1: CLIENTES
    # =========================================================================
    def _setup_tab_clientes(self):
        frame_form = ttk.LabelFrame(self.tab_clientes, text="Registrar Nuevo Cliente", padding=12)
        frame_form.pack(fill="x", padx=12, pady=10)

        ttk.Label(frame_form, text="ID Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.ent_cli_id = ttk.Entry(frame_form, width=22)
        self.ent_cli_id.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(frame_form, text="Nombre Completo:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.ent_cli_nombre = ttk.Entry(frame_form, width=30)
        self.ent_cli_nombre.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(frame_form, text="Correo Electrónico:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_cli_email = ttk.Entry(frame_form, width=22)
        self.ent_cli_email.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(frame_form, text="Teléfono:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_cli_tel = ttk.Entry(frame_form, width=30)
        self.ent_cli_tel.grid(row=1, column=3, padx=5, pady=4)

        btn_registrar = tk.Button(
            frame_form,
            text="Registrar Cliente",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._registrar_cliente,
        )
        btn_registrar.grid(row=2, column=0, columnspan=4, pady=8)

        frame_lista = ttk.LabelFrame(self.tab_clientes, text="Clientes Registrados en Memoria", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "nombre", "email", "telefono")
        self.tree_clientes = ttk.Treeview(frame_lista, columns=cols, show="headings", height=12)
        self.tree_clientes.heading("id", text="ID")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("email", text="Correo Electrónico")
        self.tree_clientes.heading("telefono", text="Teléfono")

        self.tree_clientes.column("id", width=100, anchor="center")
        self.tree_clientes.column("nombre", width=240)
        self.tree_clientes.column("email", width=260)
        self.tree_clientes.column("telefono", width=150, anchor="center")
        self.tree_clientes.pack(fill="both", expand=True)

    def _registrar_cliente(self):
        cli_id = self.ent_cli_id.get().strip()
        nombre = self.ent_cli_nombre.get().strip()
        email = self.ent_cli_email.get().strip()
        tel = self.ent_cli_tel.get().strip()

        try:
            if any(c.get_id() == cli_id for c in self.clientes):
                raise SoftwareFJError(f"Ya existe un cliente registrado con el ID '{cli_id}'", "ID_DUPLICADO")

            nuevo_cliente = Client(cli_id, nombre, email, tel)
            self.clientes.append(nuevo_cliente)
            logger.info(f"Cliente registrado desde GUI: {nuevo_cliente.get_description()}")

            self.ent_cli_id.delete(0, tk.END)
            self.ent_cli_nombre.delete(0, tk.END)
            self.ent_cli_email.delete(0, tk.END)
            self.ent_cli_tel.delete(0, tk.END)

            self._refrescar_todo()
            messagebox.showinfo("Registro Exitoso", f"Cliente '{nuevo_cliente.get_name()}' registrado correctamente.")
        except SoftwareFJError as error:
            log_error(logger, error, "Error al registrar cliente desde GUI")
            messagebox.showerror("Error de Validación", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado al registrar cliente desde GUI")
            messagebox.showerror("Error Inesperado", str(error))

    # =========================================================================
    # PESTAÑA 2: SERVICIOS
    # =========================================================================
    def _setup_tab_servicios(self):
        frame_form = ttk.LabelFrame(self.tab_servicios, text="Crear Nuevo Servicio", padding=12)
        frame_form.pack(fill="x", padx=12, pady=10)

        ttk.Label(frame_form, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.cmb_tipo_srv = ttk.Combobox(
            frame_form,
            state="readonly",
            width=25,
            values=["Reserva de Sala", "Alquiler de Equipos", "Asesoría Especializada"],
        )
        self.cmb_tipo_srv.current(0)
        self.cmb_tipo_srv.grid(row=0, column=1, padx=5, pady=4)
        self.cmb_tipo_srv.bind("<<ComboboxSelected>>", self._actualizar_label_extra_srv)

        ttk.Label(frame_form, text="ID Servicio:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.ent_srv_id = ttk.Entry(frame_form, width=22)
        self.ent_srv_id.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(frame_form, text="Nombre Servicio:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_srv_nombre = ttk.Entry(frame_form, width=28)
        self.ent_srv_nombre.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(frame_form, text="Costo Base ($):").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_srv_costo = ttk.Entry(frame_form, width=22)
        self.ent_srv_costo.grid(row=1, column=3, padx=5, pady=4)

        self.lbl_srv_extra = ttk.Label(frame_form, text="Número de Sala (entero):")
        self.lbl_srv_extra.grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.ent_srv_extra = ttk.Entry(frame_form, width=28)
        self.ent_srv_extra.grid(row=2, column=1, padx=5, pady=4)

        btn_crear_srv = tk.Button(
            frame_form,
            text="Agregar Servicio",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._crear_servicio,
        )
        btn_crear_srv.grid(row=2, column=2, columnspan=2, pady=6)

        frame_lista = ttk.LabelFrame(self.tab_servicios, text="Catálogo de Servicios Disponibles", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "tipo", "nombre", "costo", "detalle")
        self.tree_servicios = ttk.Treeview(frame_lista, columns=cols, show="headings", height=12)
        self.tree_servicios.heading("id", text="ID")
        self.tree_servicios.heading("tipo", text="Tipo")
        self.tree_servicios.heading("nombre", text="Servicio")
        self.tree_servicios.heading("costo", text="Costo Base")
        self.tree_servicios.heading("detalle", text="Descripción / Stock")

        self.tree_servicios.column("id", width=80, anchor="center")
        self.tree_servicios.column("tipo", width=150)
        self.tree_servicios.column("nombre", width=180)
        self.tree_servicios.column("costo", width=110, anchor="e")
        self.tree_servicios.column("detalle", width=340)
        self.tree_servicios.pack(fill="both", expand=True)

    def _actualizar_label_extra_srv(self, _event=None):
        tipo = self.cmb_tipo_srv.get()
        if tipo == "Reserva de Sala":
            self.lbl_srv_extra.config(text="Número de Sala (entero):")
        elif tipo == "Alquiler de Equipos":
            self.lbl_srv_extra.config(text="Stock Inicial (entero):")
        else:
            self.lbl_srv_extra.config(text="Nombre del Consultor:")

    def _crear_servicio(self):
        tipo = self.cmb_tipo_srv.get()
        srv_id = self.ent_srv_id.get().strip()
        nombre = self.ent_srv_nombre.get().strip()
        costo_str = self.ent_srv_costo.get().strip()
        extra_str = self.ent_srv_extra.get().strip()

        try:
            if any(s.get_id() == srv_id for s in self.servicios):
                raise SoftwareFJError(f"Ya existe un servicio con ID '{srv_id}'", "ID_DUPLICADO")

            try:
                costo = float(costo_str)
            except ValueError as err:
                raise SoftwareFJError("El costo base debe ser un valor numérico válido.", "DATO_INVALIDO") from err

            if tipo == "Reserva de Sala":
                try:
                    num_sala = int(extra_str)
                except ValueError as err:
                    raise SoftwareFJError("El número de sala debe ser un número entero.", "DATO_INVALIDO") from err
                servicio = ReserveRoom(srv_id, nombre, costo, num_sala)

            elif tipo == "Alquiler de Equipos":
                try:
                    stock = int(extra_str)
                except ValueError as err:
                    raise SoftwareFJError("El stock debe ser un número entero.", "DATO_INVALIDO") from err
                servicio = RentEquipment(srv_id, nombre, costo, stock)

            else:
                servicio = SpecializedConsulting(srv_id, nombre, costo, extra_str)

            self.servicios.append(servicio)
            logger.info(f"Servicio creado desde GUI: {servicio.get_description()}")

            self.ent_srv_id.delete(0, tk.END)
            self.ent_srv_nombre.delete(0, tk.END)
            self.ent_srv_costo.delete(0, tk.END)
            self.ent_srv_extra.delete(0, tk.END)

            self._refrescar_todo()
            messagebox.showinfo("Servicio Creado", f"Servicio '{servicio.get_name()}' agregado al catálogo.")
        except SoftwareFJError as error:
            log_error(logger, error, "Error al crear servicio desde GUI")
            messagebox.showerror("Error en Servicio", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado al crear servicio desde GUI")
            messagebox.showerror("Error Inesperado", str(error))

    # =========================================================================
    # PESTAÑA 3: RESERVAS
    # =========================================================================
    def _setup_tab_reservas(self):
        frame_top = ttk.LabelFrame(self.tab_reservas, text="Nueva Reserva", padding=10)
        frame_top.pack(fill="x", padx=12, pady=8)

        ttk.Label(frame_top, text="ID Reserva:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.ent_res_id = ttk.Entry(frame_top, width=15)
        self.ent_res_id.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(frame_top, text="Cliente:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.cmb_res_cliente = ttk.Combobox(frame_top, state="readonly", width=28)
        self.cmb_res_cliente.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(frame_top, text="Servicio:").grid(row=0, column=4, sticky="w", padx=5, pady=4)
        self.cmb_res_servicio = ttk.Combobox(frame_top, state="readonly", width=30)
        self.cmb_res_servicio.grid(row=0, column=5, padx=5, pady=4)

        ttk.Label(frame_top, text="Duración (hrs/días):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_res_duracion = ttk.Entry(frame_top, width=15)
        self.ent_res_duracion.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(frame_top, text="Unidades (solo equipos):").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_res_unidades = ttk.Entry(frame_top, width=15)
        self.ent_res_unidades.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        btn_crear_res = tk.Button(
            frame_top,
            text="Crear Reserva (Pendiente)",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._crear_reserva,
        )
        btn_crear_res.grid(row=1, column=4, columnspan=2, pady=6)

        frame_acciones = ttk.LabelFrame(
            self.tab_reservas, text="Gestionar Reserva Seleccionada (Confirmar / Procesar / Cancelar)", padding=10
        )
        frame_acciones.pack(fill="x", padx=12, pady=6)

        ttk.Label(frame_acciones, text="Impuesto (0.0 - 1.0, ej: 0.19):").pack(side="left", padx=5)
        self.ent_tax = ttk.Entry(frame_acciones, width=8)
        self.ent_tax.insert(0, "0.19")
        self.ent_tax.pack(side="left", padx=5)

        ttk.Label(frame_acciones, text="Descuento (0.0 - 0.5, ej: 0.10):").pack(side="left", padx=5)
        self.ent_discount = ttk.Entry(frame_acciones, width=8)
        self.ent_discount.insert(0, "0.0")
        self.ent_discount.pack(side="left", padx=5)

        tk.Button(
            frame_acciones, text="1. Confirmar", bg="#f39c12", fg="white", command=self._confirmar_reserva
        ).pack(side="left", padx=6)
        tk.Button(
            frame_acciones, text="2. Procesar Cobro", bg="#27ae60", fg="white", command=self._procesar_reserva
        ).pack(side="left", padx=6)
        tk.Button(
            frame_acciones, text="Cancelar Reserva", bg="#c0392b", fg="white", command=self._cancelar_reserva
        ).pack(side="left", padx=6)

        # Tabla de reservas
        frame_lista = ttk.LabelFrame(self.tab_reservas, text="Reservas en el Sistema", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "cliente", "servicio", "duracion", "unidades", "estado", "total")
        self.tree_reservas = ttk.Treeview(frame_lista, columns=cols, show="headings", height=10)
        self.tree_reservas.heading("id", text="ID")
        self.tree_reservas.heading("cliente", text="Cliente")
        self.tree_reservas.heading("servicio", text="Servicio")
        self.tree_reservas.heading("duracion", text="Duración")
        self.tree_reservas.heading("unidades", text="Unidades")
        self.tree_reservas.heading("estado", text="Estado")
        self.tree_reservas.heading("total", text="Total ($)")

        self.tree_reservas.column("id", width=80, anchor="center")
        self.tree_reservas.column("cliente", width=160)
        self.tree_reservas.column("servicio", width=210)
        self.tree_reservas.column("duracion", width=80, anchor="center")
        self.tree_reservas.column("unidades", width=80, anchor="center")
        self.tree_reservas.column("estado", width=110, anchor="center")
        self.tree_reservas.column("total", width=110, anchor="e")
        self.tree_reservas.pack(fill="both", expand=True)

    def _crear_reserva(self):
        res_id = self.ent_res_id.get().strip()
        idx_cli = self.cmb_res_cliente.current()
        idx_srv = self.cmb_res_servicio.current()
        dur_str = self.ent_res_duracion.get().strip()
        uni_str = self.ent_res_unidades.get().strip()

        try:
            if any(r.get_id() == res_id for r in self.reservas):
                raise SoftwareFJError(f"Ya existe una reserva con el ID '{res_id}'", "ID_DUPLICADO")

            cliente = self.clientes[idx_cli] if idx_cli >= 0 else None
            servicio = self.servicios[idx_srv] if idx_srv >= 0 else None

            try:
                duracion = float(dur_str) if "." in dur_str else int(dur_str)
            except ValueError:
                duracion = dur_str  # Se pasa para que Reservation.validate() lance InvalidDataError

            units = None
            if uni_str != "":
                try:
                    units = int(uni_str)
                except ValueError:
                    units = uni_str

            nueva_reserva = Reservation(res_id, cliente, servicio, duracion, units=units)
            self.reservas.append(nueva_reserva)

            self.ent_res_id.delete(0, tk.END)
            self.ent_res_duracion.delete(0, tk.END)
            self.ent_res_unidades.delete(0, tk.END)

            self._refrescar_todo()
            messagebox.showinfo("Reserva Creada", f"Reserva '{res_id}' registrada en estado PENDIENTE.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Crear Reserva", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado creando reserva en GUI")
            messagebox.showerror("Error Inesperado", str(error))

    def _obtener_reserva_seleccionada(self):
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Seleccione una reserva de la tabla primero.")
            return None
        res_id = self.tree_reservas.item(seleccion[0])["values"][0]
        for r in self.reservas:
            if r.get_id() == str(res_id):
                return r
        return None

    def _confirmar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            reserva.confirm()
            self._refrescar_todo()
            messagebox.showinfo("Confirmada", f"La reserva {reserva.get_id()} ha sido CONFIRMADA.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Confirmar", str(error))

    def _procesar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            tax_str = self.ent_tax.get().strip()
            disc_str = self.ent_discount.get().strip()

            tax_rate = float(tax_str) if tax_str else None
            discount = float(disc_str) if disc_str else None

            total = reserva.process(tax_rate=tax_rate, discount=discount)
            self._refrescar_todo()
            messagebox.showinfo("Reserva Procesada", f"Reserva {reserva.get_id()} procesada.\nTotal: ${total:,.2f}")
        except ValueError:
            messagebox.showerror("Dato Inválido", "Impuesto y descuento deben ser valores numéricos.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Procesar", str(error))

    def _cancelar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            reserva.cancel()
            self._refrescar_todo()
            messagebox.showinfo("Cancelada", f"La reserva {reserva.get_id()} fue CANCELADA.")
        except SoftwareFJError as error:
            messagebox.showerror("Operación No Permitida", str(error))

    # =========================================================================
    # PESTAÑA 4: SIMULACIÓN Y LOGS
    # =========================================================================
    def _setup_tab_simulacion_logs(self):
        frame_botones = tk.Frame(self.tab_simulacion_logs)
        frame_botones.pack(fill="x", padx=12, pady=10)

        tk.Button(
            frame_botones,
            text="Ejecutar Simulación Completa (12 Operaciones)",
            bg="#8e44ad",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self._correr_simulacion,
        ).pack(side="left", padx=5)

        tk.Button(
            frame_botones,
            text="Refrescar Archivo de Logs",
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self._cargar_logs,
        ).pack(side="left", padx=5)

        self.txt_logs = scrolledtext.ScrolledText(
            self.tab_simulacion_logs, width=115, height=28, font=("Consolas", 9), bg="#1e1e1e", fg="#dcdcdc"
        )
        self.txt_logs.pack(fill="both", expand=True, padx=12, pady=6)

    def _correr_simulacion(self):
        try:
            self.clientes, self.servicios, self.reservas = ejecutar_simulacion(
                self.clientes, self.servicios, self.reservas
            )
            self._refrescar_todo()
            messagebox.showinfo(
                "Simulación Finalizada",
                "La simulación se ejecutó y se actualizaron las listas en memoria.",
            )
        except Exception as error:
            log_error(logger, error, "Error ejecutando simulación desde GUI")
            messagebox.showerror("Error", f"Ocurrió un fallo en la simulación: {error}")

    def _cargar_logs(self):
        self.txt_logs.delete("1.0", tk.END)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as archivo:
                self.txt_logs.insert(tk.END, archivo.read())
            self.txt_logs.see(tk.END)
        else:
            self.txt_logs.insert(tk.END, "Aún no existe el archivo de logs. Ejecute una operación o simulación.")

    # =========================================================================
    # SINCRONIZACIÓN DE TABLAS Y COMBOBOXES
    # =========================================================================
    def _refrescar_todo(self):
        # Clientes
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.clientes:
            self.tree_clientes.insert("", tk.END, values=(c.get_id(), c.get_name(), c.get_email(), c.get_phone()))

        self.cmb_res_cliente["values"] = [f"{c.get_id()} - {c.get_name()}" for c in self.clientes]
        if self.clientes and self.cmb_res_cliente.current() == -1:
            self.cmb_res_cliente.current(0)

        # Servicios
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        for s in self.servicios:
            tipo = type(s).__name__
            self.tree_servicios.insert(
                "", tk.END, values=(s.get_id(), tipo, s.get_name(), f"${s.get_cost():,.2f}", s.get_description())
            )

        self.cmb_res_servicio["values"] = [f"{s.get_id()} - {s.get_name()}" for s in self.servicios]
        if self.servicios and self.cmb_res_servicio.current() == -1:
            self.cmb_res_servicio.current(0)

        # Reservas
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for r in self.reservas:
            unidades = r.get_units() if r.get_units() is not None else "N/A"
            self.tree_reservas.insert(
                "",
                tk.END,
                values=(
                    r.get_id(),
                    r.get_client().get_name(),
                    r.get_service().get_name(),
                    r.get_duration(),
                    unidades,
                    r.get_status(),
                    f"${r.get_total_cost():,.2f}",
                ),
            )

        self._cargar_logs()


if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJApp(root)
    root.mainloop()