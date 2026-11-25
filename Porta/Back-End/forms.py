# FORMULARIOS DEL PORTAFOLIO (Flask-WTF)
# Cada clase es un formulario. Flask-WTF se encarga de tres cosas:
# 1. Dibujar los campos en el HTML
# 2. Validar lo que escribe la persona
# 3. Agregar el token CSRF a cada formulario (proteccion de seguridad)

# FlaskForm es la clase de la que heredan todos los formularios.
# FileField y FileAllowed sirven para subir archivos y limitar su tipo
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

# Tipos de campo: texto corto, contrasena, boton, texto largo,
# casilla (si/no), numero y lista donde se eligen varias opciones
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
                     BooleanField, IntegerField, SelectMultipleField)

# Validadores: reglas que tiene que cumplir cada campo
# DataRequired: no puede quedar vacio
# Length: minimo y maximo de caracteres
# Email: tiene que tener formato de correo (usa la libreria email-validator)
# Optional: se puede dejar vacio
from wtforms.validators import DataRequired, Length, Email, Optional


# FORMULARIO DE LOGIN (pagina /login)
# Solo hay usuario y contrasena. No hay registro publico: mi usuario
# lo cree una sola vez desde un script
class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])
    password = PasswordField("Contrasena", validators=[DataRequired(), Length(min=6)])
    enviar = SubmitField("Ingresar")


# FORMULARIO DE CONTACTO (pagina /contacto)
# Lo que se envia se guarda en la tabla mensajes_contacto
class ContactoForm(FlaskForm):
    # El maximo de caracteres coincide con el tamano de la columna en la base
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    # El asunto es opcional, por eso no lleva DataRequired
    asunto = StringField("Asunto", validators=[Length(max=150)])
    # TextAreaField es el cuadro grande de texto. Pido un minimo de 10 letras
    mensaje = TextAreaField("Mensaje", validators=[DataRequired(), Length(min=10)])
    enviar = SubmitField("Enviar mensaje")


# FORMULARIO PARA CREAR Y EDITAR PROYECTOS (panel de administracion)
# Casi todos los campos son opcionales, menos el titulo
class ProyectoForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=150)])
    categoria = StringField("Categoría", validators=[Optional(), Length(max=100)])
    descripcion_corta = TextAreaField("Descripción corta", validators=[Optional()])
    descripcion_completa = TextAreaField("Descripción completa", validators=[Optional()])
    url_demo = StringField("Link a la demo", validators=[Optional(), Length(max=255)])
    url_repositorio = StringField("Link al repositorio", validators=[Optional(), Length(max=255)])

    # Imagen de portada. FileAllowed limita los formatos que se pueden subir
    imagen = FileField("Imagen de portada", validators=[
        FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes jpg, png o webp")
    ])

    # Lista donde se eligen varias tecnologias que ya existen. Las opciones
    # no estan aca: se cargan desde la base en la ruta (app.py).
    # coerce=int convierte lo que llega (texto) en numeros, que son los ids
    tecnologias_ids = SelectMultipleField("Tecnologías (Ctrl para elegir varias)", coerce=int)

    # Para agregar tecnologias nuevas, separadas por coma. La ruta las crea
    otras_tecnologias = StringField("Otras tecnologías (separadas por coma)", validators=[Optional()])

    # Casillas: destacado hace que salga en el inicio, publicado que se vea en la web
    destacado = BooleanField("Mostrar en el inicio")
    publicado = BooleanField("Publicado", default=True)

    # Numero para ordenar los proyectos, el 0 aparece primero
    orden = IntegerField("Orden (0 aparece primero)", validators=[Optional()])
    enviar = SubmitField("Guardar proyecto")


# FORMULARIO PARA EDITAR LOS TEXTOS DEL INICIO (panel de administracion)
# Cada campo corresponde a una columna de la tabla contenido_home.
# Asi puedo cambiar los textos de la pagina sin tocar el codigo
class ContenidoHomeForm(FlaskForm):
    etiqueta_hero = StringField("Etiqueta de arriba", validators=[Optional(), Length(max=100)])
    # La barra | separa la parte normal del titulo de la parte que va en color
    titulo_hero = StringField("Título principal (la barra | separa la parte en rojo)",
                              validators=[Optional(), Length(max=255)])
    descripcion_hero = TextAreaField("Descripción del inicio", validators=[Optional()])
    texto_tarjeta_superior = StringField("Texto superior de la tarjeta", validators=[Optional(), Length(max=150)])
    titulo_tarjeta = StringField("Título de la tarjeta", validators=[Optional(), Length(max=150)])
    descripcion_tarjeta = TextAreaField("Descripción de la tarjeta", validators=[Optional()])
    etiqueta_sobre_mi = StringField("Etiqueta de Sobre mí", validators=[Optional(), Length(max=100)])
    titulo_sobre_mi = StringField("Título de Sobre mí", validators=[Optional(), Length(max=255)])
    descripcion_sobre_mi = TextAreaField("Texto de Sobre mí", validators=[Optional()])
    titulo_experiencia = StringField("Título de Experiencia", validators=[Optional(), Length(max=255)])
    titulo_educacion = StringField("Título de Educación", validators=[Optional(), Length(max=255)])
    titulo_habilidades = StringField("Título de Habilidades", validators=[Optional(), Length(max=255)])
    titulo_proyectos = StringField("Título de Proyectos", validators=[Optional(), Length(max=255)])
    titulo_contacto = StringField("Título de Contacto", validators=[Optional(), Length(max=255)])
    descripcion_contacto = TextAreaField("Descripción de Contacto", validators=[Optional()])
    enviar = SubmitField("Guardar cambios")


# FORMULARIO PARA EDITAR MIS DATOS PERSONALES Y SUBIR EL CV (panel)
# Corresponde a la tabla perfil
class PerfilForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    titulo_profesional = StringField("Título profesional", validators=[Optional(), Length(max=150)])
    descripcion_corta = TextAreaField("Descripción corta", validators=[Optional()])
    descripcion_personal = TextAreaField("Descripción personal", validators=[Optional()])
    email_contacto = StringField("Email de contacto", validators=[Optional(), Email(), Length(max=150)])
    ubicacion = StringField("Ubicación", validators=[Optional(), Length(max=100)])
    disponible_trabajar = BooleanField("Disponible para trabajar")
    # Solo se aceptan archivos PDF para el CV
    cv = FileField("CV en PDF", validators=[FileAllowed(["pdf"], "Solo archivos PDF")])
    enviar = SubmitField("Guardar perfil")