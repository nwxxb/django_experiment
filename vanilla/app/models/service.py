from app.database import db
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Service(db.Model):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    doctor_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    doctor: Mapped["User"] = relationship(back_populates='services')

    def to_dict(self, attach_assoc=True):
        result = {
                'id': self.id,
                'name': self.name,
                'address': self.address,
        }

        if attach_assoc:
            result['doctor'] = self.doctor.to_dict()

        return result
