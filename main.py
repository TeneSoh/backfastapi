from fastapi import FastAPI
from routes.contacts import maincontacts
from routes.auth import auth

app = FastAPI()

# @app.get('/first-test')
# async def getData():
#    age = 89
#    return {'prenom':"lyonnel", "age":age} 

# @app.post('/store-data')
# async def storeData(data):
#    return {"data":data}

app.include_router(auth.route)
app.include_router(maincontacts.router)