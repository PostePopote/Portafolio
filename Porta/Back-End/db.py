from flask_sqlalchemy import SQLAlchemy

# Creo el objeto de la base de datos una sola vez, aca. Lo uso en app.py
# (para conectarlo con Flask) y en models.py (para definir las tablas).
# Lo separe en su propio archivo para que no se importen entre ellos
# y den error.
db = SQLAlchemy()