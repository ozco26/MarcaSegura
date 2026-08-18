from app.config.extensions import db
from app.models.incident import Incident


def CreateIncident(
    user_id,
    description,
    severity,
):
    incident = Incident(
        user_id=user_id,
        description=description,
        severity=severity,
    )

    db.session.add(incident)

    return incident
