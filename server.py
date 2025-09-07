# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# 🔧 Import your entrypoint. Adjust to match your code.
# For example, if you have a function that runs the pipeline:
#   from open_deep_research.deep_researcher import run_research
# If yours looks different, adapt the call inside /research.
from open_deep_research.deep_researcher import run_research  # <-- adjust if needed

app = FastAPI(title="ODR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class Query(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research")
def research(q: Query):
    # Return whatever your pipeline returns (dict/str). Adapt as needed.
    return run_research(q.question)
