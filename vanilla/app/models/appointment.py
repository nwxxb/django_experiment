from app.database import db
from sqlalchemy import String, Numeric, ForeignKey, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

class NumericToFloat(TypeDecorator):
    impl = Numeric

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return float(value)

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(primary_key=True)
    scheduled_at: Mapped[float] = mapped_column(NumericToFloat(precision=15, scale=6), nullable=False)

    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'), nullable=False)
    service: Mapped["Service"] = relationship(back_populates='appointments')

    doctor_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    doctor: Mapped["User"] = relationship(back_populates='assignations', foreign_keys=[doctor_id])

    patient_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    patient: Mapped["User"] = relationship(back_populates='appointments', foreign_keys=[patient_id])

    def to_dict(self, attach_assoc=[]):
        result = {
                'id': self.id,
                'scheduled_at': self.scheduled_at
        }

        if 'service' in attach_assoc:
            result['service'] = self.service.to_dict()

        if 'doctor' in attach_assoc:
            result['doctor'] = self.doctor.to_dict()

        if 'patient' in attach_assoc:
            result['patient'] = self.patient.to_dict()

        return result
