
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db


# Clase base que comparten los modelos. Contiene métodos comunes
# para guardar, eliminar y mostrar información de los registros.
# Al ser abstracta, no genera una tabla propia en la base de datos.
class ModeloBase(db.Model):
    __abstract__ = True

    # Cada modelo define su propia forma de mostrar un resumen.
    def resumen(self):
        raise NotImplementedError("Cada modelo debe definir su resumen")

    # Guarda los cambios del objeto en la base de datos.
    def guardar(self):
        db.session.add(self)
        db.session.commit()

    # Elimina el objeto de la base de datos.
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    # Muestra el nombre del modelo y un resumen de sus datos.
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.resumen()}>"


# Tabla intermedia que permite relacionar proyectos con varias tecnologías.
proyecto_tecnologias = db.Table(
    "proyecto_tecnologias",
    db.Column("id_proyecto", db.Integer,
    db.ForeignKey("proyectos.id_proyecto", ondelete="CASCADE"),
    primary_key=True),
    db.Column("id_tecnologia", db.Integer,
    db.ForeignKey("tecnologias.id_tecnologia", ondelete="CASCADE"),
    primary_key=True),
)


# Usuario hereda de ModeloBase para utilizar sus métodos y de UserMixin
# para poder trabajar con el sistema de inicio de sesión de Flask-Login.
class Usuario(UserMixin, ModeloBase):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)

    # La contraseña se almacena como un hash y no como texto plano.
    # El guion bajo indica que es un atributo de uso interno.
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    ultimo_acceso = db.Column(db.DateTime)

    # Flask-Login utiliza este método para identificar al usuario.
    def get_id(self):
        return str(self.id_usuario)

    # Evita que se pueda consultar directamente la contraseña.
    @property
    def password(self):
        raise AttributeError("La contrasena no se puede leer")

    # Cuando se asigna una contraseña, se guarda su versión cifrada.
    @password.setter
    def password(self, texto_plano):
        self._password_hash = generate_password_hash(texto_plano)

    # Comprueba si la contraseña ingresada coincide con el hash guardado.
    def verificar_password(self, texto_plano):
        return check_password_hash(self._password_hash, texto_plano)

    # Devuelve un resumen con el nombre y el correo del usuario.
    def resumen(self):
        return f"{self.username} ({self.email})"


class Perfil(ModeloBase):
    __tablename__ = "perfil"

    id_perfil = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    titulo_profesional = db.Column(db.String(150))
    descripcion_corta = db.Column(db.Text)
    descripcion_personal = db.Column(db.Text)
    email_contacto = db.Column(db.String(150))
    ubicacion = db.Column(db.String(100))
    disponible_trabajar = db.Column(db.Boolean, default=False)
    foto_perfil = db.Column(db.String(255))
    ruta_cv = db.Column(db.String(255))
    fecha_actualizacion = db.Column(db.DateTime, server_default=db.func.now(),
                                    onupdate=db.func.now())

    # Muestra el nombre y el título profesional del perfil.
    def resumen(self):
        return f"{self.nombre} - {self.titulo_profesional}"


class RedSocial(ModeloBase):
    __tablename__ = "redes_sociales"

    id_red = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icono = db.Column(db.String(100))
    visible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    # Devuelve el nombre de la red social y su enlace.
    def resumen(self):
        return f"{self.nombre}: {self.url}"


class ContenidoHome(ModeloBase):
    __tablename__ = "contenido_home"

    id_contenido = db.Column(db.Integer, primary_key=True)
    etiqueta_hero = db.Column(db.String(100))
    titulo_hero = db.Column(db.String(255))
    descripcion_hero = db.Column(db.Text)
    titulo_tarjeta = db.Column(db.String(150))
    descripcion_tarjeta = db.Column(db.Text)
    texto_tarjeta_superior = db.Column(db.String(150))
    etiqueta_sobre_mi = db.Column(db.String(100))
    titulo_sobre_mi = db.Column(db.String(255))
    descripcion_sobre_mi = db.Column(db.Text)
    titulo_experiencia = db.Column(db.String(255))
    titulo_educacion = db.Column(db.String(255))
    titulo_habilidades = db.Column(db.String(255))
    titulo_proyectos = db.Column(db.String(255))
    titulo_contacto = db.Column(db.String(255))
    descripcion_contacto = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, server_default=db.func.now(),
                                    onupdate=db.func.now())

    # Muestra el título principal de la página de inicio.
    def resumen(self):
        return f"Home: {self.titulo_hero}"


class ContenidoProyectos(ModeloBase):
    __tablename__ = "contenido_proyectos"

    id_contenido = db.Column(db.Integer, primary_key=True)
    etiqueta = db.Column(db.String(100))
    titulo = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, server_default=db.func.now(),
    onupdate=db.func.now())

    # Devuelve el título de la página de proyectos.
    def resumen(self):
        return f"Pagina proyectos: {self.titulo}"


class Experiencia(ModeloBase):
    __tablename__ = "experiencias"

    id_experiencia = db.Column(db.Integer, primary_key=True)
    puesto = db.Column(db.String(150), nullable=False)
    empresa = db.Column(db.String(150))
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    actual = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    # Muestra el puesto y la empresa donde se trabajó.
    def resumen(self):
        return f"{self.puesto} en {self.empresa}"


class Educacion(ModeloBase):
    __tablename__ = "educacion"

    id_educacion = db.Column(db.Integer, primary_key=True)
    institucion = db.Column(db.String(150), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    visible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    # Devuelve el título obtenido y la institución correspondiente.
    def resumen(self):
        return f"{self.titulo} - {self.institucion}"


class Habilidad(ModeloBase):
    __tablename__ = "habilidades"

    id_habilidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100))
    nivel = db.Column(db.String(50))
    descripcion = db.Column(db.String(255))
    visible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    # Muestra el nombre de la habilidad junto con su nivel.
    def resumen(self):
        return f"{self.nombre} ({self.nivel})"


class Tecnologia(ModeloBase):
    __tablename__ = "tecnologias"

    id_tecnologia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    icono = db.Column(db.String(100))

    # En este caso, el resumen solamente devuelve el nombre.
    def resumen(self):
        return self.nombre


class Proyecto(ModeloBase):
    __tablename__ = "proyectos"

    id_proyecto = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), nullable=False, unique=True)
    categoria = db.Column(db.String(100))
    descripcion_corta = db.Column(db.Text)
    descripcion_completa = db.Column(db.Text)
    imagen_portada = db.Column(db.String(255))
    url_demo = db.Column(db.String(255))
    url_repositorio = db.Column(db.String(255))
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    destacado = db.Column(db.Boolean, default=False)
    publicado = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_actualizacion = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Un proyecto puede tener varias imágenes asociadas.
    # Si se elimina el proyecto, también se eliminan sus imágenes.
    imagenes = db.relationship("ImagenProyecto", backref="proyecto",
    cascade="all, delete-orphan", order_by="ImagenProyecto.orden")

    # Un proyecto puede utilizar varias tecnologías y una tecnología
    # también puede estar presente en diferentes proyectos.
    tecnologias = db.relationship("Tecnologia", secondary=proyecto_tecnologias,backref="proyectos")

    # Muestra el título del proyecto y la categoría a la que pertenece.
    def resumen(self):
        return f"{self.titulo} [{self.categoria}]"


class ImagenProyecto(ModeloBase):
    __tablename__ = "imagenes_proyectos"

    id_imagen = db.Column(db.Integer, primary_key=True)
    id_proyecto = db.Column(db.Integer,
                            db.ForeignKey("proyectos.id_proyecto", ondelete="CASCADE"),
                            nullable=False)
    ruta_imagen = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255))
    orden = db.Column(db.Integer, default=0)

    # Devuelve la ruta donde se encuentra guardada la imagen.
    def resumen(self):
        return f"Imagen: {self.ruta_imagen}"


class MensajeContacto(ModeloBase):
    __tablename__ = "mensajes_contacto"

    id_mensaje = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    asunto = db.Column(db.String(150))
    mensaje = db.Column(db.Text, nullable=False)
    fecha_recepcion = db.Column(db.DateTime, server_default=db.func.now())
    estado = db.Column(db.String(30), default="nuevo")

    # Muestra quién envió el mensaje y cuál fue el asunto.
    def resumen(self):
        return f"{self.nombre}: {self.asunto}"
