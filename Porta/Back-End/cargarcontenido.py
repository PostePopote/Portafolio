from app import app
from models import (Perfil, ContenidoHome, ContenidoProyectos, RedSocial, Habilidad, Educacion)

with app.app_context():
    # Datos personales, cambia nombre y email por los tuyos
    Perfil(
        nombre="NOMBRE",
        titulo_profesional="Estudiante de programación",
        descripcion_corta="Estudiante de programación que busca su primera experiencia.",
        descripcion_personal="Me gusta el Front End y el CSS, y estoy aprendiendo a llevar mis proyectos a la web.",
        email_contacto="email@gmail.com",
        ubicacion="Córdoba, Argentina",
        disponible_trabajar=True
    ).guardar()

    # Textos del inicio, en el titulo la barra | separa la parte que va en rojo
    ContenidoHome(
        etiqueta_hero="Buscando mi primera experiencia",
        titulo_hero="Ideas distintas.|Problemas resueltos.",
        descripcion_hero="Estudiante de programación que construye aplicaciones con Python, Flask, Django, MySQL y JavaScript.",
        titulo_tarjeta="Aprender, comprobar que funcione y mejorar",
        descripcion_tarjeta="Vamos por partes",
        texto_tarjeta_superior="Explorar. Crear. Conectar.",
        etiqueta_sobre_mi="01 / Sobre mí",
        titulo_sobre_mi="Multiples soluciones en una mirada",
        descripcion_sobre_mi=(
            "Me gusta aportar ideas y distintas perspectivas para resolver problemas. "
            "Disfruto del Front End y del CSS, y ahora estoy aprendiendo a llevar mis "
            "proyectos a la web. Fuera de la programación, mi interés es estudiar "
            "medicina y convertirme en anestesiólogo."
        ),
        titulo_experiencia="El recorrido también cuenta.",
        titulo_educacion="Aprender. Hacer. Volver a aprender.",
        titulo_habilidades="Herramientas y formas de trabajar.",
        titulo_proyectos="Proyectos con personalidad.",
        titulo_contacto="Lo bueno comienza con una oportunidad.",
        descripcion_contacto="¿Estas interesado? Escribime."
    ).guardar()

    ContenidoProyectos(
        etiqueta="Mis trabajos",
        titulo="Todos mis proyectos.",
        descripcion="Trabajos hechos durante la tecnicatura."
    ).guardar()

    # Educacion de ejemplo, falta la ronda 2
    Educacion(institucion="ESCUELA", titulo="Tecnicatura en Programación",
    descripcion="Programación, bases de datos y desarrollo web.",
    tipo="Carrera").guardar()

    # Habilidades tecnicas (nivel intermedio) y blandas
    tecnicas = ["Python", "MySQL", "HTML / CSS", "Flask", "Django", "JavaScript", "Git / GitHub"]
    blandas = ["Comunicación efectiva", "Resolución de problemas y pensamiento crítico",
    "Adaptabilidad", "Gestión del tiempo"]

    orden = 0
    for nombre in tecnicas:
        Habilidad(nombre=nombre, nivel="Intermedio", categoria="Técnica", orden=orden).guardar()
        orden += 1
    for nombre in blandas:
        Habilidad(nombre=nombre, nivel="Blanda", categoria="Blanda", orden=orden).guardar()
        orden += 1

    # Redes de ejemplo, falta la ronda 2
    RedSocial(nombre="GitHub", url="https://github.com/PostePopote", icono="fa-brands fa-github", orden=1).guardar()
    RedSocial(nombre="LinkedIn", url="https://linkedin.com/", icono="fa-brands fa-linkedin", orden=2).guardar()

    print("Contenido cargado")