from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.redis import init_redis, close_redis
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Redis
    await init_redis()
    yield
    # Shutdown: Close Redis
    await close_redis()

app = FastAPI(
    title="PSF to Stripe Integration Backend",
    lifespan=lifespan
)

# Register our routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Stripe Integration Service is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)