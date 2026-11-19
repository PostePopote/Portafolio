from app import app
from models import Usuario

with app.app_context():
    admin = Usuario(username="Francisco Loforte La Gala", email="d48670430@alumnos.itr.edu.ar")
    # El setter de password guarda el hash, no la contrasena real
    admin.password = "PostePopote_2020"
    admin.guardar()
    print("Admin creado:", admin)