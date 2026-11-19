# Guía rápida: excepciones y logs

Esta guía explica cómo usar en **tu módulo** (clientes, servicios, main, etc.) las herramientas que ya están creadas para:

1. **Lanzar errores claros** → `models/exceptions.py`
2. **Registrar eventos y errores en un archivo** → `utils/logger.py`

> Así todo el proyecto maneja los errores **de la misma forma** y todo queda guardado en un solo archivo: `logs/software_fj.log`.

---

## 1. ¿Qué excepción uso?

Elige según **qué salió mal**:

| Si el problema es...                                  | Usa                         | Cómo se crea                                          |
|-------------------------------------------------------|-----------------------------|-------------------------------------------------------|
| Un dato está mal (vacío, negativo, formato incorrecto) | `InvalidDataError`          | `InvalidDataError("El correo no es válido")`          |
| Falta un dato obligatorio                              | `MissingParameterError`     | `MissingParameterError("name")` ← solo el nombre del dato |
| Se intenta hacer algo que no se puede                  | `OperationNotAllowedError`  | `OperationNotAllowedError("El cliente ya existe")`    |
| Falló una reserva                                      | `ReservationError`          | `ReservationError("No se pudo reservar")`             |
| El servicio no está disponible                         | `ServiceUnavailableError`   | `ServiceUnavailableError("Proyector")` ← solo el nombre del servicio |
| Un cálculo da un resultado ilógico                     | `CalculationError`          | `CalculationError("El costo no puede ser negativo")`  |

Todas son "hijas" de **`SoftwareFJError`**. Eso significa que con un solo `except SoftwareFJError` las atrapas todas.

Cuando se imprimen se ven así:

```
[DATO_INVALIDO] El correo no es válido
[PARAMETRO_FALTANTE] Falta el parámetro obligatorio: 'name'
```

---

## 2. Lanzar una excepción (en tus clases)

### Paso 1: importar

```python
from models.exceptions import InvalidDataError, MissingParameterError
```

### Paso 2: usar `raise` cuando algo esté mal

Ejemplo en una clase `Client`:

```python
class Client(Entity):
    def validate(self):
        if not self.__name:
            raise MissingParameterError("name")
        if "@" not in self.__email:
            raise InvalidDataError("El correo no es válido")
```

Ejemplo en un servicio (en lugar de `ValueError`):

```python
def set_cost(self, cost):
    if cost < 0:
        raise InvalidDataError("El costo no puede ser negativo")
    self._cost = float(cost)
```

---

## 3. Registrar en el log

### Paso 1: importar y crear el logger (una vez, arriba del archivo)

```python
from utils.logger import get_logger, log_error

logger = get_logger("client")   # pon el nombre de tu módulo: "client", "service", "main"...
```

### Paso 2: registrar lo que pasa

| Para registrar...              | Usa                                   |
|--------------------------------|---------------------------------------|
| Algo que salió bien            | `logger.info("Cliente C1 registrado")` |
| Un error                       | `log_error(logger, error)`            |
| Un error con contexto          | `log_error(logger, error, "Registro de cliente C1")` |
| Detalles internos (opcional)   | `logger.debug("Validando datos...")`  |

En el archivo `logs/software_fj.log` queda así:

```
2026-11-14 09:19:32 | INFO     | software_fj.client | Cliente C1 registrado
2026-11-14 09:19:32 | ERROR    | software_fj.client | Registro de cliente C2: [DATO_INVALIDO] El correo no es válido
```

> La carpeta `logs/` se crea sola. No hay que hacer nada más.

---

## 4. Atrapar errores sin que el programa se caiga

Este es el patrón que debe usarse (por ejemplo en `main.py`):

```python
from models.exceptions import SoftwareFJError
from utils.logger import get_logger, log_error

logger = get_logger("main")

try:
    client = Client("C1", "Ana", "ana@correo.com")
except SoftwareFJError as error:
    log_error(logger, error, "Registro de cliente")
    print(f"No se pudo registrar: {error}")
else:
    logger.info("Cliente registrado correctamente")
finally:
    print("Operación terminada")
```

| Bloque    | Se ejecuta...                        |
|-----------|--------------------------------------|
| `try`     | Siempre: aquí va lo que puede fallar |
| `except`  | Solo si hubo error                   |
| `else`    | Solo si **no** hubo error            |
| `finally` | Siempre, haya o no error             |

---

## 5. Encadenar excepciones (`raise ... from ...`)

Sirve para **convertir** un error técnico de Python en uno nuestro **sin perder** el error original.

```python
from models.exceptions import InvalidDataError

try:
    age = int(text_age)
except ValueError as error:
    raise InvalidDataError(f"La edad '{text_age}' no es un número") from error
```

Si luego registras ese error con `log_error`, en el log aparece también la causa original:

```
ERROR | ... | [DATO_INVALIDO] La edad 'veinte' no es un número | Causa original: ValueError: invalid literal for int()...
```

---

## 6. Ejemplo completo

Ver `models/reservation.py`. Ahí se usan todos los casos de esta guía:

- `validate()` → lanza `MissingParameterError` e `InvalidDataError`
- `confirm()` → `try/except/else` + encadenamiento
- `process()` → `try/except/else/finally`
- `calculate_base_cost()` → convierte `ValueError` en `CalculationError` con `from`

Y `demo_reservation.py` muestra cómo usar la clase atrapando los errores.

---

## Errores comunes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'models'` | Ejecuta el programa desde la carpeta raíz del proyecto (`fase4`), no desde dentro de `models/`. |
| `ModuleNotFoundError: No module named 'service'` | Cambia `from service import Service` por `from models.service import Service`. |
| El error se ve en consola pero el programa se detiene | Te faltó envolver la operación en `try/except SoftwareFJError`. |
| No aparece nada en el log | Revisa que estés usando `logger.info(...)` o `log_error(...)`, no solo `print(...)`. |
