from sqlalchemy import Column, Integer, String

from database import base


class Contact(base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(255), nullable=False)
    pays = Column(String(255), nullable=False)
    image = Column(String(255), nullable=True)