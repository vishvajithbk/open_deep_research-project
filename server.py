# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from importlib import import_module
import inspect, logging

app = FastAPI(title="ODR API")

class Query(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

def _call_entrypoint(fn, question: str):
    sig = inspect.signature(fn)
    try:
        # Try string param
        if len(sig.parameters) >= 1:
            return fn(question)
    except TypeError:
        pass
    # Try dict-style input (LangGraph conventions)
    return fn({"question": question})

@app.post("/research")
def research(q: Query):
    mod = import_module("open_deep_research.deep_researcher")
    candidates = ("run_research", "deep_research", "research", "run")
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            return _call_entrypoint(fn, q.question)
    # Class-based fallback
    for cls_name in ("DeepResearcher", "Researcher"):
        cls = getattr(mod, cls_name, None)
        if cls is not None:
            obj = cls()  # adjust if it needs args
            for meth in ("run", "invoke", "__call__"):
                if hasattr(obj, meth):
                    return _call_entrypoint(getattr(obj, meth), q.question)
    logging.error("deep_researcher has: %s",
                  [n for n in dir(mod) if not n.startswith("_")])
    raise HTTPException(500, "No suitable entrypoint found in deep_researcher")
