import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from db import db
from forms import LoginForm, ContactoForm, ProyectoForm, ContenidoHomeForm, PerfilForm
from models import (Usuario, Proyecto, MensajeContacto, Perfil, RedSocial, ContenidoHome, ContenidoProyectos, Experiencia, Educacion, Habilidad, Tecnologia)

try:
    import config
except ImportError:
    config = None

def leer(nombre, por_defecto=None):
    # Primero busco en el entorno (Render), si no esta uso config.py (mi PC)
    valor = os.getenv(nombre)
    if valor:
        return valor
    return getattr(config, nombre, por_defecto)

# Le indico a Flask donde estan los templates y los archivos estaticos
app = Flask(
    __name__,
    template_folder="../Front-End/templates",
    static_folder="../Front-End/static"
)
# Clave secreta, la necesita Flask-WTF y las sesiones del login
app.config["SECRET_KEY"] = leer("SECRET_KEY")

# Armo la direccion de conexion a MySQL, ahora con el puerto
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{leer('DB_USER')}:{leer('DB_PASSWORD')}"
    f"@{leer('DB_HOST')}:{leer('DB_PORT', '3306')}/{leer('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Pocas conexiones abiertas, porque la base gratuita permite pocas a la vez
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 2,
    "max_overflow": 0,
    "pool_recycle": 280,
    "pool_pre_ping": True,
}

# Tamano maximo de archivos subidos: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Conecto la base de datos con la app
db.init_app(app)

# Proteccion CSRF para todos los formularios, incluidos los botones de borrar
csrf = CSRFProtect(app)

# Configuro Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# Si alguien entra a una pagina protegida sin sesion, lo mando al login
login_manager.login_view = "login"

# Flask-Login usa esta funcion para recuperar al usuario de la sesion
@login_manager.user_loader
def cargar_usuario(id_usuario):
    return db.session.get(Usuario, int(id_usuario))

# Esta funcion hace que perfil y redes esten disponibles en TODOS los templates
@app.context_processor
def datos_globales():
    return {
        "perfil": Perfil.query.first(),
        "redes": RedSocial.query.filter_by(visible=True).order_by(RedSocial.orden).all()
    }

# Convierte un titulo en un slug: "Mi Proyecto" -> "mi-proyecto"
def crear_slug(texto):
    return texto.lower().strip().replace(" ", "-")

# Guarda un archivo subido dentro de static y devuelve la ruta relativa
def guardar_archivo(archivo, carpeta):
    # secure_filename limpia el nombre para que no se pueda colar una ruta peligrosa
    nombre = secure_filename(archivo.filename)
    nombre = f"{int(datetime.now().timestamp())}_{nombre}"
    destino = os.path.join(app.static_folder, carpeta)
    # Si la carpeta no existe, la crea
    os.makedirs(destino, exist_ok=True)
    archivo.save(os.path.join(destino, nombre))
    return f"{carpeta}/{nombre}"

# Rutas de las paginas
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

@app.route("/proyectos")
def proyectos():
    lista = Proyecto.query.filter_by(publicado=True).order_by(Proyecto.orden).all()
    return render_template("proyectos.html", proyectos=lista, contenido=ContenidoProyectos.query.first())

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    form = ContactoForm()

    if form.validate_on_submit():
        # Creo el mensaje con los datos del formulario y lo guardo en la base
        nuevo = MensajeContacto(
            nombre=form.nombre.data,
            email=form.email.data,
            asunto=form.asunto.data,
            mensaje=form.mensaje.data
        )
        nuevo.guardar()
        flash("Mensaje enviado, gracias por escribirme", "exito")
        return redirect(url_for("contacto"))

    return render_template("contacto.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Si ya inicio sesion no hace falta mostrar el login
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    # validate_on_submit revisa el CSRF y las validaciones del formulario
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()

        # Comparo la contrasena escrita con el hash guardado
        if usuario and usuario.verificar_password(form.password.data):
            login_user(usuario)
            usuario.ultimo_acceso = datetime.now()
            db.session.commit()
            return redirect(url_for("home"))

        flash("Usuario o contrasena incorrectos", "error")

    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# Panel principal de administracion
@app.route("/admin")
@login_required
def admin():
    lista = Proyecto.query.order_by(Proyecto.orden).all()
    return render_template("admin.html", proyectos=lista)

# Esta misma funcion sirve para crear (sin id) y para editar (con id)
@app.route("/admin/proyecto/nuevo", methods=["GET", "POST"])
@app.route("/admin/proyecto/<int:id_proyecto>/editar", methods=["GET", "POST"])
@login_required
def editar_proyecto(id_proyecto=None):
    if id_proyecto:
        proyecto = db.get_or_404(Proyecto, id_proyecto)
    else:
        proyecto = Proyecto()

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

        proyecto.tecnologias = elegidas
        proyecto.guardar()
        flash("Proyecto guardado", "exito")
        return redirect(url_for("admin"))

    return render_template("editarproyecto.html", form=form, proyecto=proyecto)

# El borrado va por POST para que no se pueda disparar con solo abrir un link
@app.route("/admin/proyecto/<int:id_proyecto>/borrar", methods=["POST"])
@login_required
def borrar_proyecto(id_proyecto):
    proyecto = db.get_or_404(Proyecto, id_proyecto)
    proyecto.eliminar()
    flash("Proyecto eliminado", "exito")
    return redirect(url_for("admin"))

# Editar los textos del inicio
@app.route("/editar-home", methods=["GET", "POST"])
@login_required
def editar_home():
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
        archivo = form.cv.data
        if archivo and archivo.filename:
            perfil_actual.ruta_cv = guardar_archivo(archivo, "docs")
        db.session.commit()
        flash("Perfil actualizado", "exito")
        return redirect(url_for("admin"))

    return render_template("editarperfil.html", form=form)

if __name__ == "__main__":
    app.run(debug=False)