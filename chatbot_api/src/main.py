from fastapi import FastAPI
from routers.user_router import router as auth_router
from routers.chat_router import router as chat_router
app = FastAPI(
    title="Bike Shop ChatBot",
    description="Bike Shop ChatBot",
)
app.include_router(auth_router)
app.include_router(chat_router)


