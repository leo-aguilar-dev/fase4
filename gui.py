import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from models.client import Client
from models.exceptions import SoftwareFJError
from models.reservation import Reservation
from models.service_rent_equipment import RentEquipment
from models.service_reserve_room import ReserveRoom
from models.service_specialized_consulting import SpecializedConsulting
from simulation import run_simulation
from utils.logger import LOG_FILE, get_logger, log_error

logger = get_logger("gui")


class SoftwareFJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión Orientado a Objetos")
        self.root.geometry("980x680")
        self.root.minsize(900, 620)

        self.clients = []
        self.services = []
        self.reservations = []

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
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

        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_services = ttk.Frame(self.notebook)
        self.tab_reservations = ttk.Frame(self.notebook)
        self.tab_simulation_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clients, text="1. Clientes")
        self.notebook.add(self.tab_services, text="2. Servicios")
        self.notebook.add(self.tab_reservations, text="3. Reservas")
        self.notebook.add(self.tab_simulation_logs, text="4. Simulación y Logs")

        self._setup_clients_tab()
        self._setup_services_tab()
        self._setup_reservations_tab()
        self._setup_simulation_logs_tab()

    # =========================================================================
    # PESTAÑA 1: CLIENTES
    # =========================================================================
    def _setup_clients_tab(self):
        form_frame = ttk.LabelFrame(self.tab_clients, text="Registrar Nuevo Cliente", padding=12)
        form_frame.pack(fill="x", padx=12, pady=10)

        ttk.Label(form_frame, text="ID Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.ent_cli_id = ttk.Entry(form_frame, width=22)
        self.ent_cli_id.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form_frame, text="Nombre Completo:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.ent_cli_name = ttk.Entry(form_frame, width=30)
        self.ent_cli_name.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form_frame, text="Correo Electrónico:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_cli_email = ttk.Entry(form_frame, width=22)
        self.ent_cli_email.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form_frame, text="Teléfono:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_cli_phone = ttk.Entry(form_frame, width=30)
        self.ent_cli_phone.grid(row=1, column=3, padx=5, pady=4)

        btn_register = tk.Button(
            form_frame,
            text="Registrar Cliente",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._register_client,
        )
        btn_register.grid(row=2, column=0, columnspan=4, pady=8)

        list_frame = ttk.LabelFrame(self.tab_clients, text="Clientes Registrados en Memoria", padding=10)
        list_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "name", "email", "phone")
        self.tree_clients = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        self.tree_clients.heading("id", text="ID")
        self.tree_clients.heading("name", text="Nombre")
        self.tree_clients.heading("email", text="Correo Electrónico")
        self.tree_clients.heading("phone", text="Teléfono")

        self.tree_clients.column("id", width=100, anchor="center")
        self.tree_clients.column("name", width=240)
        self.tree_clients.column("email", width=260)
        self.tree_clients.column("phone", width=150, anchor="center")
        self.tree_clients.pack(fill="both", expand=True)

    def _register_client(self):
        client_id = self.ent_cli_id.get().strip()
        name = self.ent_cli_name.get().strip()
        email = self.ent_cli_email.get().strip()
        phone = self.ent_cli_phone.get().strip()

        try:
            if any(c.get_id() == client_id for c in self.clients):
                raise SoftwareFJError(f"Ya existe un cliente registrado con el ID '{client_id}'", "ID_DUPLICADO")

            new_client = Client(client_id, name, email, phone)
            self.clients.append(new_client)
            logger.info(f"Cliente registrado desde GUI: {new_client.get_description()}")

            self.ent_cli_id.delete(0, tk.END)
            self.ent_cli_name.delete(0, tk.END)
            self.ent_cli_email.delete(0, tk.END)
            self.ent_cli_phone.delete(0, tk.END)

            self._refresh_all()
            messagebox.showinfo("Registro Exitoso", f"Cliente '{new_client.get_name()}' registrado correctamente.")
        except SoftwareFJError as error:
            log_error(logger, error, "Error al registrar cliente desde GUI")
            messagebox.showerror("Error de Validación", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado al registrar cliente desde GUI")
            messagebox.showerror("Error Inesperado", str(error))

    # =========================================================================
    # PESTAÑA 2: SERVICIOS
    # =========================================================================
    def _setup_services_tab(self):
        form_frame = ttk.LabelFrame(self.tab_services, text="Crear Nuevo Servicio", padding=12)
        form_frame.pack(fill="x", padx=12, pady=10)

        ttk.Label(form_frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.cmb_srv_type = ttk.Combobox(
            form_frame,
            state="readonly",
            width=25,
            values=["Reserva de Sala", "Alquiler de Equipos", "Asesoría Especializada"],
        )
        self.cmb_srv_type.current(0)
        self.cmb_srv_type.grid(row=0, column=1, padx=5, pady=4)
        self.cmb_srv_type.bind("<<ComboboxSelected>>", self._update_srv_extra_label)

        ttk.Label(form_frame, text="ID Servicio:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.ent_srv_id = ttk.Entry(form_frame, width=22)
        self.ent_srv_id.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form_frame, text="Nombre Servicio:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_srv_name = ttk.Entry(form_frame, width=28)
        self.ent_srv_name.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form_frame, text="Costo Base ($):").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_srv_cost = ttk.Entry(form_frame, width=22)
        self.ent_srv_cost.grid(row=1, column=3, padx=5, pady=4)

        self.lbl_srv_extra = ttk.Label(form_frame, text="Número de Sala (entero):")
        self.lbl_srv_extra.grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.ent_srv_extra = ttk.Entry(form_frame, width=28)
        self.ent_srv_extra.grid(row=2, column=1, padx=5, pady=4)

        btn_create_srv = tk.Button(
            form_frame,
            text="Agregar Servicio",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._create_service,
        )
        btn_create_srv.grid(row=2, column=2, columnspan=2, pady=6)

        list_frame = ttk.LabelFrame(self.tab_services, text="Catálogo de Servicios Disponibles", padding=10)
        list_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "type", "name", "cost", "detail")
        self.tree_services = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        self.tree_services.heading("id", text="ID")
        self.tree_services.heading("type", text="Tipo")
        self.tree_services.heading("name", text="Servicio")
        self.tree_services.heading("cost", text="Costo Base")
        self.tree_services.heading("detail", text="Descripción / Stock")

        self.tree_services.column("id", width=80, anchor="center")
        self.tree_services.column("type", width=150)
        self.tree_services.column("name", width=180)
        self.tree_services.column("cost", width=110, anchor="e")
        self.tree_services.column("detail", width=340)
        self.tree_services.pack(fill="both", expand=True)

    def _update_srv_extra_label(self, _event=None):
        srv_type = self.cmb_srv_type.get()
        if srv_type == "Reserva de Sala":
            self.lbl_srv_extra.config(text="Número de Sala (entero):")
        elif srv_type == "Alquiler de Equipos":
            self.lbl_srv_extra.config(text="Stock Inicial (entero):")
        else:
            self.lbl_srv_extra.config(text="Nombre del Consultor:")

    def _create_service(self):
        srv_type = self.cmb_srv_type.get()
        srv_id = self.ent_srv_id.get().strip()
        name = self.ent_srv_name.get().strip()
        cost_str = self.ent_srv_cost.get().strip()
        extra_str = self.ent_srv_extra.get().strip()

        try:
            if any(s.get_id() == srv_id for s in self.services):
                raise SoftwareFJError(f"Ya existe un servicio con ID '{srv_id}'", "ID_DUPLICADO")

            try:
                cost = float(cost_str)
            except ValueError as err:
                raise SoftwareFJError("El costo base debe ser un valor numérico válido.", "DATO_INVALIDO") from err

            if srv_type == "Reserva de Sala":
                try:
                    room_number = int(extra_str)
                except ValueError as err:
                    raise SoftwareFJError("El número de sala debe ser un número entero.", "DATO_INVALIDO") from err
                service = ReserveRoom(srv_id, name, cost, room_number)

            elif srv_type == "Alquiler de Equipos":
                try:
                    stock = int(extra_str)
                except ValueError as err:
                    raise SoftwareFJError("El stock debe ser un número entero.", "DATO_INVALIDO") from err
                service = RentEquipment(srv_id, name, cost, stock)

            else:
                service = SpecializedConsulting(srv_id, name, cost, extra_str)

            self.services.append(service)
            logger.info(f"Servicio creado desde GUI: {service.get_description()}")

            self.ent_srv_id.delete(0, tk.END)
            self.ent_srv_name.delete(0, tk.END)
            self.ent_srv_cost.delete(0, tk.END)
            self.ent_srv_extra.delete(0, tk.END)

            self._refresh_all()
            messagebox.showinfo("Servicio Creado", f"Servicio '{service.get_name()}' agregado al catálogo.")
        except SoftwareFJError as error:
            log_error(logger, error, "Error al crear servicio desde GUI")
            messagebox.showerror("Error en Servicio", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado al crear servicio desde GUI")
            messagebox.showerror("Error Inesperado", str(error))

    # =========================================================================
    # PESTAÑA 3: RESERVAS
    # =========================================================================
    def _setup_reservations_tab(self):
        top_frame = ttk.LabelFrame(self.tab_reservations, text="Nueva Reserva", padding=10)
        top_frame.pack(fill="x", padx=12, pady=8)

        ttk.Label(top_frame, text="ID Reserva:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.ent_res_id = ttk.Entry(top_frame, width=15)
        self.ent_res_id.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(top_frame, text="Cliente:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.cmb_res_client = ttk.Combobox(top_frame, state="readonly", width=28)
        self.cmb_res_client.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(top_frame, text="Servicio:").grid(row=0, column=4, sticky="w", padx=5, pady=4)
        self.cmb_res_service = ttk.Combobox(top_frame, state="readonly", width=30)
        self.cmb_res_service.grid(row=0, column=5, padx=5, pady=4)

        ttk.Label(top_frame, text="Duración (hrs/días):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.ent_res_duration = ttk.Entry(top_frame, width=15)
        self.ent_res_duration.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(top_frame, text="Unidades (solo equipos):").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ent_res_units = ttk.Entry(top_frame, width=15)
        self.ent_res_units.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        btn_create_res = tk.Button(
            top_frame,
            text="Crear Reserva (Pendiente)",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self._create_reservation,
        )
        btn_create_res.grid(row=1, column=4, columnspan=2, pady=6)

        actions_frame = ttk.LabelFrame(
            self.tab_reservations, text="Gestionar Reserva Seleccionada (Confirmar / Procesar / Cancelar)", padding=10
        )
        actions_frame.pack(fill="x", padx=12, pady=6)

        ttk.Label(actions_frame, text="Impuesto (0.0 - 1.0, ej: 0.19):").pack(side="left", padx=5)
        self.ent_tax = ttk.Entry(actions_frame, width=8)
        self.ent_tax.insert(0, "0.19")
        self.ent_tax.pack(side="left", padx=5)

        ttk.Label(actions_frame, text="Descuento (0.0 - 0.5, ej: 0.10):").pack(side="left", padx=5)
        self.ent_discount = ttk.Entry(actions_frame, width=8)
        self.ent_discount.insert(0, "0.0")
        self.ent_discount.pack(side="left", padx=5)

        tk.Button(
            actions_frame, text="1. Confirmar", bg="#f39c12", fg="white", command=self._confirm_reservation
        ).pack(side="left", padx=6)
        tk.Button(
            actions_frame, text="2. Procesar Cobro", bg="#27ae60", fg="white", command=self._process_reservation
        ).pack(side="left", padx=6)
        tk.Button(
            actions_frame, text="Cancelar Reserva", bg="#c0392b", fg="white", command=self._cancel_reservation
        ).pack(side="left", padx=6)

        # Tabla de reservas
        list_frame = ttk.LabelFrame(self.tab_reservations, text="Reservas en el Sistema", padding=10)
        list_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "client", "service", "duration", "units", "status", "total")
        self.tree_reservations = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        self.tree_reservations.heading("id", text="ID")
        self.tree_reservations.heading("client", text="Cliente")
        self.tree_reservations.heading("service", text="Servicio")
        self.tree_reservations.heading("duration", text="Duración")
        self.tree_reservations.heading("units", text="Unidades")
        self.tree_reservations.heading("status", text="Estado")
        self.tree_reservations.heading("total", text="Total ($)")

        self.tree_reservations.column("id", width=80, anchor="center")
        self.tree_reservations.column("client", width=160)
        self.tree_reservations.column("service", width=210)
        self.tree_reservations.column("duration", width=80, anchor="center")
        self.tree_reservations.column("units", width=80, anchor="center")
        self.tree_reservations.column("status", width=110, anchor="center")
        self.tree_reservations.column("total", width=110, anchor="e")
        self.tree_reservations.pack(fill="both", expand=True)

    def _create_reservation(self):
        res_id = self.ent_res_id.get().strip()
        cli_idx = self.cmb_res_client.current()
        srv_idx = self.cmb_res_service.current()
        dur_str = self.ent_res_duration.get().strip()
        units_str = self.ent_res_units.get().strip()

        try:
            if any(r.get_id() == res_id for r in self.reservations):
                raise SoftwareFJError(f"Ya existe una reserva con el ID '{res_id}'", "ID_DUPLICADO")

            client = self.clients[cli_idx] if cli_idx >= 0 else None
            service = self.services[srv_idx] if srv_idx >= 0 else None

            try:
                duration = float(dur_str) if "." in dur_str else int(dur_str)
            except ValueError:
                duration = dur_str  # Se pasa para que Reservation.validate() lance InvalidDataError

            units = None
            if units_str != "":
                try:
                    units = int(units_str)
                except ValueError:
                    units = units_str

            new_reservation = Reservation(res_id, client, service, duration, units=units)
            self.reservations.append(new_reservation)

            self.ent_res_id.delete(0, tk.END)
            self.ent_res_duration.delete(0, tk.END)
            self.ent_res_units.delete(0, tk.END)

            self._refresh_all()
            messagebox.showinfo("Reserva Creada", f"Reserva '{res_id}' registrada en estado PENDIENTE.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Crear Reserva", str(error))
        except Exception as error:
            log_error(logger, error, "Error inesperado creando reserva en GUI")
            messagebox.showerror("Error Inesperado", str(error))

    def _get_selected_reservation(self):
        selection = self.tree_reservations.selection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Seleccione una reserva de la tabla primero.")
            return None
        res_id = self.tree_reservations.item(selection[0])["values"][0]
        for r in self.reservations:
            if r.get_id() == str(res_id):
                return r
        return None

    def _confirm_reservation(self):
        reservation = self._get_selected_reservation()
        if not reservation:
            return
        try:
            reservation.confirm()
            self._refresh_all()
            messagebox.showinfo("Confirmada", f"La reserva {reservation.get_id()} ha sido CONFIRMADA.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Confirmar", str(error))

    def _process_reservation(self):
        reservation = self._get_selected_reservation()
        if not reservation:
            return
        try:
            tax_str = self.ent_tax.get().strip()
            disc_str = self.ent_discount.get().strip()

            tax_rate = float(tax_str) if tax_str else None
            discount = float(disc_str) if disc_str else None

            total = reservation.process(tax_rate=tax_rate, discount=discount)
            self._refresh_all()
            messagebox.showinfo("Reserva Procesada", f"Reserva {reservation.get_id()} procesada.\nTotal: ${total:,.2f}")
        except ValueError:
            messagebox.showerror("Dato Inválido", "Impuesto y descuento deben ser valores numéricos.")
        except SoftwareFJError as error:
            messagebox.showerror("Error al Procesar", str(error))

    def _cancel_reservation(self):
        reservation = self._get_selected_reservation()
        if not reservation:
            return
        try:
            reservation.cancel()
            self._refresh_all()
            messagebox.showinfo("Cancelada", f"La reserva {reservation.get_id()} fue CANCELADA.")
        except SoftwareFJError as error:
            messagebox.showerror("Operación No Permitida", str(error))

    # =========================================================================
    # PESTAÑA 4: SIMULACIÓN Y LOGS
    # =========================================================================
    def _setup_simulation_logs_tab(self):
        buttons_frame = tk.Frame(self.tab_simulation_logs)
        buttons_frame.pack(fill="x", padx=12, pady=10)

        tk.Button(
            buttons_frame,
            text="Ejecutar Simulación Completa (12 Operaciones)",
            bg="#8e44ad",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self._run_simulation,
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Refrescar Archivo de Logs",
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self._load_logs,
        ).pack(side="left", padx=5)

        self.txt_logs = scrolledtext.ScrolledText(
            self.tab_simulation_logs, width=115, height=28, font=("Consolas", 9), bg="#1e1e1e", fg="#dcdcdc"
        )
        self.txt_logs.pack(fill="both", expand=True, padx=12, pady=6)

    def _run_simulation(self):
        try:
            self.clients, self.services, self.reservations = run_simulation(
                self.clients, self.services, self.reservations
            )
            self._refresh_all()
            messagebox.showinfo(
                "Simulación Finalizada",
                "La simulación se ejecutó y se actualizaron las listas en memoria.",
            )
        except Exception as error:
            log_error(logger, error, "Error ejecutando simulación desde GUI")
            messagebox.showerror("Error", f"Ocurrió un fallo en la simulación: {error}")

    def _load_logs(self):
        self.txt_logs.delete("1.0", tk.END)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                self.txt_logs.insert(tk.END, log_file.read())
            self.txt_logs.see(tk.END)
        else:
            self.txt_logs.insert(tk.END, "Aún no existe el archivo de logs. Ejecute una operación o simulación.")

    # =========================================================================
    # SINCRONIZACIÓN DE TABLAS Y COMBOBOXES
    # =========================================================================
    def _refresh_all(self):
        # Clientes
        for item in self.tree_clients.get_children():
            self.tree_clients.delete(item)
        for c in self.clients:
            self.tree_clients.insert("", tk.END, values=(c.get_id(), c.get_name(), c.get_email(), c.get_phone()))

        self.cmb_res_client["values"] = [f"{c.get_id()} - {c.get_name()}" for c in self.clients]
        if self.clients and self.cmb_res_client.current() == -1:
            self.cmb_res_client.current(0)

        # Servicios
        for item in self.tree_services.get_children():
            self.tree_services.delete(item)
        for s in self.services:
            srv_type = type(s).__name__
            self.tree_services.insert(
                "", tk.END, values=(s.get_id(), srv_type, s.get_name(), f"${s.get_cost():,.2f}", s.get_description())
            )

        self.cmb_res_service["values"] = [f"{s.get_id()} - {s.get_name()}" for s in self.services]
        if self.services and self.cmb_res_service.current() == -1:
            self.cmb_res_service.current(0)

        # Reservas
        for item in self.tree_reservations.get_children():
            self.tree_reservations.delete(item)
        for r in self.reservations:
            units = r.get_units() if r.get_units() is not None else "N/A"
            self.tree_reservations.insert(
                "",
                tk.END,
                values=(
                    r.get_id(),
                    r.get_client().get_name(),
                    r.get_service().get_name(),
                    r.get_duration(),
                    units,
                    r.get_status(),
                    f"${r.get_total_cost():,.2f}",
                ),
            )

        self._load_logs()


if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJApp(root)
    root.mainloop()