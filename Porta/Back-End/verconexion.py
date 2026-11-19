from app import app

# Muestro solo host, puerto y base, sin usuario ni contrasena
direccion = app.config["SQLALCHEMY_DATABASE_URI"]
print(direccion.split("@")[1])