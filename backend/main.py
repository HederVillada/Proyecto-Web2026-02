from fastapi import FastAPI #the app framework
from routers import equipment, auth, dashboard
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(equipment.router, prefix="/api/equipment", tags=["equipment"]) #equipment CRUD under /api/equipment
app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) #login under /api/auth
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"]) #este es para el dashboard

