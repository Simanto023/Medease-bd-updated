from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, medicines

app = FastAPI(
    title="MedEase BD API",
    description="Medicine Information Chatbot API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(medicines.router, prefix="/api/v1", tags=["medicines"])


@app.on_event("startup")
async def startup_event():
    print("🚀 MedEase BD Backend starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 MedEase BD Backend shutting down...")


@app.get("/")
async def root():
    return {"message": "Welcome to MedEase BD API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
