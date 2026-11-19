from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField, BooleanField, IntegerField, SelectMultipleField)
from wtforms.validators import DataRequired, Length, Email, Optional

# Formulario de login, FlaskForm agrega la proteccion CSRF automaticamente
class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])
    password = PasswordField("Contrasena", validators=[DataRequired(), Length(min=6)])
    enviar = SubmitField("Ingresar")

# Formulario de contacto, guarda los mensajes en la tabla mensajes_contacto
class ContactoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    asunto = StringField("Asunto", validators=[Length(max=150)])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired(), Length(min=10)])
    enviar = SubmitField("Enviar mensaje")

# Formulario para crear y editar proyectos
class ProyectoForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=150)])
    categoria = StringField("Categoría", validators=[Optional(), Length(max=100)])
    descripcion_corta = TextAreaField("Descripción corta", validators=[Optional()])
    descripcion_completa = TextAreaField("Descripción completa", validators=[Optional()])
    url_demo = StringField("Link a la demo", validators=[Optional(), Length(max=255)])
    url_repositorio = StringField("Link al repositorio", validators=[Optional(), Length(max=255)])
    # Imagen de portada, solo se aceptan estos formatos
    imagen = FileField("Imagen de portada", validators=[
        FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes jpg, png o webp")
    ])
    # Lista para elegir tecnologias que ya existen (las opciones se cargan en la ruta)
    tecnologias_ids = SelectMultipleField("Tecnologías (Ctrl para elegir varias)", coerce=int)
    # Para agregar tecnologias nuevas separadas por coma
    otras_tecnologias = StringField("Otras tecnologías (separadas por coma)", validators=[Optional()])
    destacado = BooleanField("Mostrar en el inicio")
    publicado = BooleanField("Publicado", default=True)
    orden = IntegerField("Orden (0 aparece primero)", validators=[Optional()])
    enviar = SubmitField("Guardar proyecto")


# Formulario para editar los textos del inicio
class ContenidoHomeForm(FlaskForm):
    etiqueta_hero = StringField("Etiqueta de arriba", validators=[Optional(), Length(max=100)])
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


# Formulario para editar tus datos personales y subir el CV
class PerfilForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    titulo_profesional = StringField("Título profesional", validators=[Optional(), Length(max=150)])
    descripcion_corta = TextAreaField("Descripción corta", validators=[Optional()])
    descripcion_personal = TextAreaField("Descripción personal", validators=[Optional()])
    email_contacto = StringField("Email de contacto", validators=[Optional(), Email(), Length(max=150)])
    ubicacion = StringField("Ubicación", validators=[Optional(), Length(max=100)])
    disponible_trabajar = BooleanField("Disponible para trabajar")
    cv = FileField("CV en PDF", validators=[FileAllowed(["pdf"], "Solo archivos PDF")])
    enviar = SubmitField("Guardar perfil")