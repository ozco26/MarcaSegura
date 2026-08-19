from flask import current_app
from flask_mail import Message

from app.config.extensions import mail
from app.models.user import User


def _get_admin_emails():
    admins = User.query.filter_by(role="admin", status=True).all()
    return [admin.email for admin in admins]


def send_email(subject, recipients, body):
    if not recipients:
        current_app.logger.warning(f"No hay destinatarios para el correo: {subject}")
        return

    msg = Message(subject=subject, recipients=recipients, body=body)

    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo '{subject}': {e}")


def notify_admins_unusual_location(user, location_info):
    admin_emails = _get_admin_emails()

    subject = f"[MarcaSegura] Ubicación inusual detectada - {user.name}"
    body = (
        f"Se detectó una marca de asistencia desde una ubicación inusual.\n\n"
        f"Empleado: {user.name} ({user.email})\n"
        f"Detalles: {location_info}\n\n"
        f"Revisa la auditoría en el panel de administración."
    )

    send_email(subject, admin_emails, body)


def notify_admins_failed_attempts(user, attempts):
    admin_emails = _get_admin_emails()

    subject = f"[MarcaSegura] Múltiples intentos fallidos - {user.name}"
    body = (
        f"El usuario {user.name} ({user.email}) ha tenido {attempts} intentos "
        f"fallidos de inicio de sesión consecutivos.\n\n"
        f"Revisa la auditoría en el panel de administración."
    )

    send_email(subject, admin_emails, body)


def notify_employee_device_blocked(user, device):
    subject = "[MarcaSegura] Tu acceso ha sido bloqueado"
    body = (
        f"Hola {user.name},\n\n"
        f"Tu dispositivo (identificador: {device.device_uuid}) ha sido bloqueado "
        f"por motivos de seguridad.\n\n"
        f"Si crees que esto es un error, contacta a tu administrador."
    )

    send_email(subject, [user.email], body)