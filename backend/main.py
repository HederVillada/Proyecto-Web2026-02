from fastapi import FastAPI #the app framework
from routers import equipment, auth, dashboard
from fastapi.middleware.cors import CORSMiddleware
from routers import equipment, auth, dashboard, users, reservations #this is for users
from routers import equipment, auth, dashboard, users, reservations, categories  #categorias

app = FastAPI() #create the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow any page to call this API (fine for local dev)
    allow_methods=["*"],  # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # allow any headers (including Content-Type)
)

@app.get("/") # el chequeo de salud
def root():
    return {"status": "backend is running"} #como amo el def 

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["Loans"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])