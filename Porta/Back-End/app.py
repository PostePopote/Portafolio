# ARCHIVO PRINCIPAL DEL PORTAFOLIO
# Aca se crea la app de Flask, se conecta a la base de datos y se definen
# las rutas (las direcciones de la pagina).
#
# Recorrido de una visita, por ejemplo a /proyectos:
# 1. El navegador pide la direccion y Flask busca la ruta con @app.route
# 2. La ruta consulta la base usando las clases de models.py
# 3. Los datos se mandan al template con render_template
# 4. Jinja2 arma el HTML y se lo devuelve al navegador

# Librerias estandar de Python: os para leer variables y rutas de archivos,
# datetime para guardar fechas
import os
from datetime import datetime

# Flask: la app, los templates, las redirecciones, los mensajes y los datos que llegan
from flask import Flask, render_template, redirect, url_for, flash, request

# Flask-Login: maneja la sesion del administrador
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Flask-WTF: proteccion CSRF para todos los formularios
from flask_wtf.csrf import CSRFProtect

# Limpia el nombre de los archivos que se suben
from werkzeug.utils import secure_filename

# Mis propios archivos: db.py tiene la conexion, forms.py los formularios
# y models.py las clases que representan las tablas
from db import db
from forms import LoginForm, ContactoForm, ProyectoForm, ContenidoHomeForm, PerfilForm
from models import (Usuario, Proyecto, MensajeContacto, Perfil, RedSocial, ContenidoHome, ContenidoProyectos, Experiencia, Educacion, Habilidad, Tecnologia)

# config.py solo existe en mi PC (no se sube a GitHub).
# Si no existe, como en Render, config queda en None y no da error
try:
    import config
except ImportError:
    config = None


# Esta funcion decide de donde saco los datos privados (claves, usuario y
# host de la base). En Render los cargue como variables de entorno y en mi
# PC los leo de config.py. Asi las contrasenas nunca se suben a GitHub.
def leer(nombre, por_defecto=None):
    # Primero busco en el entorno (Render), si no esta uso config.py (mi PC)
    valor = os.getenv(nombre)
    if valor:
        return valor
    return getattr(config, nombre, por_defecto)


# Creo la aplicacion. Como mis carpetas se llaman distinto a las que Flask
# busca por defecto, le indico donde estan los templates y los archivos
# estaticos (CSS, imagenes, fuentes y CV)
app = Flask(
    __name__,
    template_folder="../Front-End/templates",
    static_folder="../Front-End/static"
)

# Clave secreta: Flask la usa para firmar la sesion del login y los
# tokens CSRF de los formularios
app.config["SECRET_KEY"] = leer("SECRET_KEY")

# Direccion de conexion a MySQL. Formato:
# mysql+mysqlconnector://usuario:contrasena@host:puerto/nombre_de_la_base
# mysqlconnector es el conector que usa SQLAlchemy para hablar con MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{leer('DB_USER')}:{leer('DB_PASSWORD')}"
    f"@{leer('DB_HOST')}:{leer('DB_PORT', '3306')}/{leer('DB_NAME')}"
)

# Desactivo un aviso de SQLAlchemy que no uso
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Pocas conexiones abiertas, porque la base gratuita de Clever Cloud permite
# pocas a la vez. pool_pre_ping revisa que la conexion siga viva antes de usarla
# y pool_recycle la renueva cada tanto
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 2,
    "max_overflow": 0,
    "pool_recycle": 280,
    "pool_pre_ping": True,
}

# Tamano maximo de archivos subidos: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Conecto la base de datos con la app (db esta creada en db.py)
db.init_app(app)

# Proteccion CSRF para todos los formularios, incluidos los botones de borrar.
# Evita que otra pagina mande formularios en mi nombre
csrf = CSRFProtect(app)

# Configuro Flask-Login, que maneja quien tiene la sesion iniciada
login_manager = LoginManager()
login_manager.init_app(app)
# Si alguien entra a una pagina protegida sin sesion, lo mando al login
login_manager.login_view = "login"


# Flask-Login usa esta funcion para recuperar al usuario a partir del id
# que guarda en la cookie de sesion
@login_manager.user_loader
def cargar_usuario(id_usuario):
    return db.session.get(Usuario, int(id_usuario))


# Esta funcion hace que perfil y redes esten disponibles en TODOS los
# templates, sin pasarlos en cada ruta. Los uso en el menu y en el pie
@app.context_processor
def datos_globales():
    return {
        "perfil": Perfil.query.first(),
        "redes": RedSocial.query.filter_by(visible=True).order_by(RedSocial.orden).all()
    }


# FUNCIONES AUXILIARES

# Convierte un titulo en un slug: "Mi Proyecto" -> "mi-proyecto"
# El slug es el nombre del proyecto en formato url y no se repite
def crear_slug(texto):
    return texto.lower().strip().replace(" ", "-")


# Guarda un archivo subido (imagen o CV) dentro de static y devuelve la
# ruta relativa, que es la que se guarda en la base de datos
def guardar_archivo(archivo, carpeta):
    # secure_filename limpia el nombre para que no se pueda colar una ruta peligrosa
    nombre = secure_filename(archivo.filename)
    # Le pongo la fecha adelante para que dos archivos con el mismo nombre no se pisen
    nombre = f"{int(datetime.now().timestamp())}_{nombre}"
    destino = os.path.join(app.static_folder, carpeta)
    # Si la carpeta no existe, la crea
    os.makedirs(destino, exist_ok=True)
    archivo.save(os.path.join(destino, nombre))
    return f"{carpeta}/{nombre}"


# RUTAS PUBLICAS (las puede ver cualquier visitante)

# Pagina de inicio. Mando al template todo lo que necesita: los textos,
# la experiencia, la educacion, las habilidades y hasta 3 proyectos destacados.
# filter_by filtra, order_by ordena por la columna orden y all() trae la lista
@app.route("/")
def home():
    return render_template(
        "home.html",
        contenido=ContenidoHome.query.first(),
        experiencias=Experiencia.query.filter_by(visible=True).order_by(Experiencia.orden).all(),
        estudios=Educacion.query.filter_by(visible=True).order_by(Educacion.orden).all(),
        habilidades=Habilidad.query.filter_by(visible=True).order_by(Habilidad.orden).all(),
        destacados=Proyecto.query.filter_by(publicado=True, destacado=True).order_by(Proyecto.orden).limit(3).all()
    )


# Pagina con todos los proyectos publicados. El template los recorre con un for
@app.route("/proyectos")
def proyectos():
    lista = Proyecto.query.filter_by(publicado=True).order_by(Proyecto.orden).all()
    return render_template("proyectos.html", proyectos=lista, contenido=ContenidoProyectos.query.first())


# Formulario de contacto. Acepta GET (mostrar el formulario) y POST (enviarlo)
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    form = ContactoForm()

    # validate_on_submit es True solo si el formulario se envio por POST,
    # el token CSRF es valido y los campos cumplen las validaciones
    if form.validate_on_submit():
        # Creo el mensaje con los datos del formulario y lo guardo en la base
        nuevo = MensajeContacto(
            nombre=form.nombre.data,
            email=form.email.data,
            asunto=form.asunto.data,
            mensaje=form.mensaje.data
        )
        # guardar() lo heredo de ModeloBase (es la herencia de POO)
        nuevo.guardar()
        flash("Mensaje enviado, gracias por escribirme", "exito")
        # Redirijo para que al recargar la pagina no se reenvie el mensaje
        return redirect(url_for("contacto"))

    return render_template("contacto.html", form=form)


# LOGIN Y LOGOUT

@app.route("/login", methods=["GET", "POST"])
def login():
    # Si ya inicio sesion no hace falta mostrar el login
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    # validate_on_submit revisa el CSRF y las validaciones del formulario
    if form.validate_on_submit():
        # Busco el usuario por su nombre
        usuario = Usuario.query.filter_by(username=form.username.data).first()

        # Comparo la contrasena escrita con el hash guardado (nunca se
        # guarda la contrasena real)
        if usuario and usuario.verificar_password(form.password.data):
            # login_user guarda la sesion en una cookie firmada con la SECRET_KEY
            login_user(usuario)
            usuario.ultimo_acceso = datetime.now()
            db.session.commit()
            return redirect(url_for("home"))

        # Mensaje generico: no digo si fallo el usuario o la contrasena
        flash("Usuario o contrasena incorrectos", "error")

    return render_template("login.html", form=form)


# login_required: solo entra quien tiene la sesion iniciada
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# PANEL DE ADMINISTRACION (todas estas rutas piden sesion iniciada)

# Pantalla principal del panel, con la lista de todos los proyectos
@app.route("/admin")
@login_required
def admin():
    lista = Proyecto.query.order_by(Proyecto.orden).all()
    return render_template("admin.html", proyectos=lista)


# Esta misma funcion sirve para crear (sin id) y para editar (con id).
# Por eso tiene dos @app.route y el id es opcional
@app.route("/admin/proyecto/nuevo", methods=["GET", "POST"])
@app.route("/admin/proyecto/<int:id_proyecto>/editar", methods=["GET", "POST"])
@login_required
def editar_proyecto(id_proyecto=None):
    # Si hay id traigo el proyecto de la base, si no creo uno vacio.
    # get_or_404 muestra error 404 si el id no existe
    if id_proyecto:
        proyecto = db.get_or_404(Proyecto, id_proyecto)
    else:
        proyecto = Proyecto()

    # obj=proyecto rellena el formulario con los datos actuales
    form = ProyectoForm(obj=proyecto)
    # Cargo las opciones de tecnologias desde la base
    form.tecnologias_ids.choices = [
        (t.id_tecnologia, t.nombre) for t in Tecnologia.query.order_by(Tecnologia.nombre)
    ]

    if request.method == "GET":
        # Al abrir el formulario marco las tecnologias que el proyecto ya tiene
        form.tecnologias_ids.data = [t.id_tecnologia for t in proyecto.tecnologias]
        # Un proyecto nuevo empieza como publicado
        if not id_proyecto:
            form.publicado.data = True

    if form.validate_on_submit():
        # Copio los datos del formulario al objeto proyecto
        proyecto.titulo = form.titulo.data
        proyecto.categoria = form.categoria.data
        proyecto.descripcion_corta = form.descripcion_corta.data
        proyecto.descripcion_completa = form.descripcion_completa.data
        proyecto.url_demo = form.url_demo.data
        proyecto.url_repositorio = form.url_repositorio.data
        proyecto.destacado = form.destacado.data
        proyecto.publicado = form.publicado.data
        proyecto.orden = form.orden.data or 0

        # El slug se crea una sola vez, y si ya existe uno igual le agrego un numero
        if not proyecto.slug:
            base = crear_slug(form.titulo.data)
            slug = base
            numero = 2
            while Proyecto.query.filter_by(slug=slug).first():
                slug = f"{base}-{numero}"
                numero += 1
            proyecto.slug = slug

        # Si subio una imagen nueva, la guardo
        archivo = form.imagen.data
        if archivo and archivo.filename:
            proyecto.imagen_portada = guardar_archivo(archivo, "img/proyectos")

        # Tecnologias elegidas de la lista
        ids = form.tecnologias_ids.data or []
        elegidas = Tecnologia.query.filter(Tecnologia.id_tecnologia.in_(ids)).all() if ids else []

        # Tecnologias nuevas escritas a mano, si no existen las creo
        for nombre in (form.otras_tecnologias.data or "").split(","):
            nombre = nombre.strip()
            if not nombre:
                continue
            # Evito repetir una tecnologia que ya esta en la lista
            if nombre.lower() in [t.nombre.lower() for t in elegidas]:
                continue
            tec = Tecnologia.query.filter_by(nombre=nombre).first()
            if not tec:
                tec = Tecnologia(nombre=nombre)
            elegidas.append(tec)

        # Asigno la lista de tecnologias: SQLAlchemy llena solo la tabla
        # intermedia proyecto_tecnologias (relacion muchos a muchos)
        proyecto.tecnologias = elegidas
        proyecto.guardar()
        flash("Proyecto guardado", "exito")
        return redirect(url_for("admin"))

    return render_template("editarproyecto.html", form=form, proyecto=proyecto)


# El borrado va por POST para que no se pueda disparar con solo abrir un link,
# y el formulario del panel lleva el token CSRF
@app.route("/admin/proyecto/<int:id_proyecto>/borrar", methods=["POST"])
@login_required
def borrar_proyecto(id_proyecto):
    proyecto = db.get_or_404(Proyecto, id_proyecto)
    # eliminar() tambien viene de ModeloBase. Por el cascade, se borran
    # solas sus imagenes y sus relaciones con tecnologias
    proyecto.eliminar()
    flash("Proyecto eliminado", "exito")
    return redirect(url_for("admin"))


# Editar los textos del inicio
@app.route("/editar-home", methods=["GET", "POST"])
@login_required
def editar_home():
    # Hay una sola fila de contenido, si no existe da error 404
    contenido = ContenidoHome.query.first_or_404()
    form = ContenidoHomeForm(obj=contenido)

    if form.validate_on_submit():
        # populate_obj copia los datos del formulario al objeto de la base
        form.populate_obj(contenido)
        db.session.commit()
        flash("Inicio actualizado", "exito")
        return redirect(url_for("admin"))

    return render_template("editarhome.html", form=form)


# Editar datos personales y subir el CV
@app.route("/editar-perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    perfil_actual = Perfil.query.first_or_404()
    form = PerfilForm(obj=perfil_actual)

    if form.validate_on_submit():
        form.populate_obj(perfil_actual)
        # Si subio un PDF nuevo lo guardo en static/docs y anoto la ruta
        archivo = form.cv.data
        if archivo and archivo.filename:
            perfil_actual.ruta_cv = guardar_archivo(archivo, "docs")
        db.session.commit()
        flash("Perfil actualizado", "exito")
        return redirect(url_for("admin"))

    return render_template("editarperfil.html", form=form)


# Solo se ejecuta si corro este archivo directo (python app.py) en mi PC.
# En Render lo levanta gunicorn y este bloque no se usa.
# debug=False para no mostrar errores internos a los visitantes
if __name__ == "__main__":
    app.run(debug=True)