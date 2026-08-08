from datetime import time

from werkzeug.security import generate_password_hash

from app import create_app
from app.config.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():

    user = User(
        name="Administrador",
        email="admin@marcasegura.com",
        password_hash=generate_password_hash("Admin123"),
        role="admin",
        status=True,
        entry_time=time(8, 0),
        exit_time=time(17, 0),
    )

    db.session.add(user)
    db.session.commit()

    print("Usuario creado correctamente")