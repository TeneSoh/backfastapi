from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from services.service import *
from models.models import Contact
from routes.auth.auth import get_current_user

router = APIRouter(prefix='/contact',tags=['Contacts'])

user_dependency = Annotated[dict ,Depends(get_current_user)]
class ContactModel(BaseModel):
    nom:str
    prenom :str
    email :str
    phone :str
    pays :str
# bonjour
@router.get('')
async def getAllContacts(db:db_dependency, user:user_dependency):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="non authentifier")
        
        contacts = db.query(Contact).all()
        return contacts
    except HTTPException as e:
        return {
            'message': 'erreur'
        }
    
    
@router.get('/{id_contact}')
async def getContactById(db:db_dependency, user:user_dependency,id_contact:int=Path(gt=0) ):
   try:
        if not user:
            raise HTTPException(status_code=401, detail="non authentifier")
        
        contact = db.query(Contact).filter(Contact.id == id_contact).first()

        return contact
   except Exception as e:
       raise HTTPException(status_code=401, detail="non authentifier")

@router.post('/storeContact')
async def storeContact(db:db_dependency, user:user_dependency,data:ContactModel):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="non authentifier")
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
    except Exception as e:
        raise HTTPException(status_code=401, detail="non authentifier")

@router.put('/editContact/{id_contact}')
async def editContact(db:db_dependency, user:user_dependency,data:ContactModel, id_contact:int = Path(gt=0)):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="non authentifier")
        
        editContact = db.query(Contact).filter(Contact.id == id_contact).first()
        if not editContact:
            raise HTTPException(status_code=404, detail='le contact n\'existe pas')
        
        # editContact.nom = str(data.nom)
        # editContact.prenom = data.prenom
        # editContact.email = data.email
        # editContact.phone = data.phone
        # editContact.pays = data.pays

        for key, value in data.model_dump().items():
            if value is not None:
                setattr(editContact, key, value) 
        # print(editContact.nom)
        # print(data.nom)
        db.commit()
        db.refresh(editContact)

        return editContact

    except Exception as e:
        print(f"erreur {e}")    

@router.delete('/delete/{id_contact}')
async def deleteContact(db:db_dependency, user:user_dependency,id_contact:int = Path(gt=0)):
    deleteContact =  editContact = db.query(Contact).filter(Contact.id == id_contact).first()

    db.delete(deleteContact)
    db.commit()

    return{
        'message': "contact supprimer avec succes",
        'contact': deleteContact
    }