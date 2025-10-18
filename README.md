 Tarea 1 - Bases de Datos

**Integrantes:**
- Iván Weber (202104092-7)
- Javier Canepa (201910028-9)

---

## Descripción

El proyecto corresponde a la **Tarea 1 del curso de Bases de Datos**, desarrollada utilizando **PostgreSQL 17** para la creación y gestión de la base de datos.  
Además, se incluyen scripts en **Python** para la generación automática de datos y la carga de estos en la base de datos.

---

## Requisitos

### Base de datos
- **PostgreSQL 17**

### Librerías de Python utilizadas
- `string`
- `secrets`
- `os`
- `dotenv`
- `psycopg2`
- `random`
- `pandas`
- `faker`
- `unicodedata`
- `datetime`

---

## Archivos del proyecto

| Archivo | Descripción |
|----------|--------------|
| `.env` | Contiene las credenciales de conexión (`DB_USER` y `DB_PASS`). No se sube al repositorio por seguridad. |
| `Generador_Datos.py` | Genera el archivo `registros.csv` con datos de prueba. |
| `CreacionBD_Poblar.py` | Crea la base de datos y pobla las tablas utilizando los datos generados. |
| `Consultas_Tarea.sql` | Contiene las consultas SQL requeridas para la evaluación de la tarea. |
| `Creacion_Tablas.sql` | Script SQL para la creación de las tablas. |
| `Modelo_Dic.pdf` | Modelo y diccionario de datos. |
| `README.md` | Archivo de instrucciones y documentación del proyecto. |

---

## Instrucciones de ejecución

1. Completar el archivo `.env` con las credenciales de conexión:
2. Ejecutar el script **`Generador_Datos.py`** para generar el archivo `registros.csv`.
3. Ejecutar el script **`CreacionBD_Poblar.py`** para crear la base de datos en PostgreSQL.
4. Ejecutar las consultas del archivo **`Consultas_Tarea.sql`** para la evaluación.

---

## Resultado esperado

Con estas instrucciones, la base de datos debería quedar creada con todas sus tablas y poblada con los datos generados en el archivo `registros.csv`.

---

*UTFSM - Ingeniería Civil Telemática*
