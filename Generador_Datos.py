import pandas as pd
import random
from faker import Faker
import unicodedata
from datetime import timedelta

# Función para limpiar acentos y caracteres especiales
def limpiar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

# Configuración
fake = Faker('es_MX')
random.seed(42)
Faker.seed(42)

# Parámetros
num_autores = 150
num_revisores = 150
num_articulos = 400
topicos = [
    "Bases de Datos", "Redes", "Inteligencia Artificial", "Estadistica", "Analisis de Sistemas",
    "Seguridad Informatica", "Desarrollo Web", "Gestion de Proyectos", "Machine Learning", "Big Data",
    "Mineria de Datos", "Computacion en la Nube", "Algoritmos", "Sistemas Operativos", "Ciberseguridad",
    "Bioinformatica", "Ingenieria de Software", "Arquitectura de Computadores", "Computacion Grafica", "Criptografia",
    "IoT", "DevOps", "Vision Computacional", "Procesamiento de Lenguaje Natural", "Robotica",
    "Sistemas Embebidos", "Blockchain", "Realidad Aumentada", "Realidad Virtual", "Compiladores",
    "Metodos Numericos", "Ingenieria de Requisitos", "Testing de Software", "Programacion Paralela", "Teoria de la Computacion",
    "Analisis de Algoritmos", "Etica en Tecnologia", "Sistemas Distribuidos", "Tecnologias Moviles", "Interaccion Humano Computador",
    "Computacion Cuantica", "Redes Neuronales", "Aprendizaje Profundo", "Data Warehousing", "Visualizacion de Datos",
    "Sistemas Recomendadores", "Automatizacion de Procesos", "Ingenieria del Conocimiento", "Analisis Forense Digital", "Análisis de Vulnerabilidades"
]


# Preparar datos
rut_base = [f"{9000000 + i}-{random.choice(['0','1','2','3','4','5','6','7','8','9','K'])}" for i in range(300)]
random.shuffle(rut_base)
autores_ruts = rut_base[:150]
revisores_ruts = rut_base[150:300]

autores = {rut: {"RUT": rut, "Nombre": limpiar(fake.name()), "Email": limpiar(fake.email())} for rut in autores_ruts}
revisores = {rut: {"RUT": rut, "Nombre": limpiar(fake.name()), "Email": limpiar(fake.email())} for rut in revisores_ruts}
topico_data = [limpiar(t) for t in topicos]

# Generar artículos
articulos = []
for _ in range(num_articulos):
    topicos_sel = random.sample(topico_data, random.randint(1, 3))
    topicos_str = "|".join(topicos_sel)

    titulo = limpiar(fake.sentence(nb_words=6))
    resumen = limpiar(fake.text(max_nb_chars=140))
    fecha_envio = fake.date_between(start_date='-2y', end_date='today')

    # Fecha de revisión aleatoria después del envío (entre 1 y 60 días)
    fecha_revision = fecha_envio + timedelta(days=random.randint(1, 60))

    autores_sel = random.sample(autores_ruts, random.randint(1, 3))
    autores_info = [f"{rut}|{autores[rut]['Nombre']}|{autores[rut]['Email']}" for rut in autores_sel]

    revisores_validos = [r for r in revisores_ruts if r not in autores_sel]
    revisores_sel = random.sample(revisores_validos, 3)
    revisores_info = [f"{rut}|{revisores[rut]['Nombre']}|{revisores[rut]['Email']}" for rut in revisores_sel]

    # Valoraciones y comentarios
    valoraciones = [str(random.randint(0, 100)) for _ in range(3)]
    comentarios = [limpiar(fake.sentence(nb_words=10)[:100]) for _ in range(3)]

    articulos.append({
        "Titulo": titulo,
        "Fecha_Envio": fecha_envio,
        "Fecha_Revision": fecha_revision,
        "Resumen": resumen,
        "Nombre_Topico": topicos_str,
        "Autores": ", ".join(autores_info),
        "Revisores": ", ".join(revisores_info),
        "Valoraciones": "|".join(valoraciones),
        "Comentarios": "|".join(comentarios)
    })

# Exportar
df_final = pd.DataFrame(articulos)
df_final.to_csv("registros.csv", index=False)

print("Archivo generado")
