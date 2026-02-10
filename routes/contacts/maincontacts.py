from pydantic import BaseModel
from fastapi import APIRouter
from services.service import *
from models.models import Contact

router = APIRouter(prefix='/contact',tags=['Contacts'])

class ContactModel(BaseModel):
    nom:str
    prenom :str
    email :str
    phone :str
    pays :str

@router.get('')
async def getAllContacts(db:db_dependency):
    contacts = db.query(Contact).all()
    return contacts

@router.get('/{id_contact}')
async def getContactById(db:db_dependency, id_contact:int=Path(gt=0) ):
    contact = db.query(Contact).filter(Contact.id == id_contact)

@router.post('/storeContact')
async def storeContact(db:db_dependency, data:ContactModel):
    new_contact = Contact(
        nom = data.nom,
        prenom = data.prenom,
        email = data.email,
        phone = data.phone,
        pays = data.pays,
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact

@router.put('/editContact/{id_contact}')
async def editContact(db:db_dependency, data:ContactModel, id_contact:int = Path(gt=0)):
    pass

@router.delete('/delete/{id_contact}')
async def deleteContact():
    pass