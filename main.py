from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, question_routes, leaderboard_routes, qna_uploader
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Bits-De-Cipher Backend", description="APIs for Bits-De-Cipher", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["AUTH"])
app.include_router(question_routes.router, prefix="/quiz", tags=["QUESTION"])
app.include_router(leaderboard_routes.router, prefix="/quiz", tags=["LEADERBOARD"])
app.include_router(qna_uploader.router, prefix="/question", tags=["QNA"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)