# Software FJ — Sistema de Gestión Orientado a Objetos

Aplicación desarrollada en Python con arquitectura modular, programación orientada a objetos, jerarquía de excepciones personalizada, registro de eventos (*logging*) e interfaz gráfica en Tkinter.

## Estructura del proyecto

- `models/`: clases de dominio (`Entity`, `Client`, `Service`, `RentEquipment`, `ReserveRoom`, `SpecializedConsulting`, `Reservation`) y excepciones (`SoftwareFJError` y derivadas).
- `utils/logger.py`: configuración del sistema de logs en consola y archivo (`logs/software_fj.log`).
- `simulacion.py`: ejecución de operaciones de prueba y validación sin interrumpir el flujo ante errores controlados.
- `gui.py`: interfaz gráfica en Tkinter para gestionar clientes, servicios, reservas y consultar logs.
- `main.py`: punto de entrada principal de la aplicación.

## Ejecución

Desde la carpeta raíz del proyecto:

```bash
python main.py