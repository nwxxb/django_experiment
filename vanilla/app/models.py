from app.database import db
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    _password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)

    def set_password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    def to_dict(self):
        return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'role': self.role.value,
        }
