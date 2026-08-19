"""
Script para crear un usuario administrador en la base de datos.

Uso (desde la raíz del proyecto, con el venv activado):
    python create_admin.py
"""

import sys
from datetime import time
from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.config.extensions import db
from app.models.user import User


def create_admin():
    app = create_app()

    with app.app_context():
        print("=== Crear usuario administrador ===\n")

        name = input("Nombre completo: ").strip()
        email = input("Correo electrónico: ").strip().lower()

        if not name or not email:
            print("\n❌ El nombre y el correo son obligatorios.")
            sys.exit(1)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"\n❌ Ya existe un usuario con el correo '{email}'.")
            sys.exit(1)

        password = getpass("Contraseña: ")
        password_confirm = getpass("Confirma la contraseña: ")

        if password != password_confirm:
            print("\n❌ Las contraseñas no coinciden.")
            sys.exit(1)

        if len(password) < 8:
            print("\n❌ La contraseña debe tener al menos 8 caracteres.")
            sys.exit(1)

        admin = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="admin",
            status=True,
            entry_time=time(0, 0),
            exit_time=time(23, 59),
        )

        db.session.add(admin)
        db.session.commit()

        print(f"\n✅ Usuario administrador '{name}' ({email}) creado exitosamente.")


if __name__ == "__main__":
    create_admin()