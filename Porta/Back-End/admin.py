from app import app
from models import Usuario

with app.app_context():
    admin = Usuario(username="NOMBRE", email="email@gmail.com")
    # El setter de password guarda el hash, no la contrasena real
    admin.password = "CONTRASEÑA"
    admin.guardar()
    print("Admin creado:", admin)