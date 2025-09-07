# src/open_deep_research/arxiv_tool.py
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import arxiv

class ArxivSearchArgs(BaseModel):
    query: str = Field(..., description='e.g., ti:"graph transformer" AND (cat:cs.LG OR cat:cs.CL)')
    max_results: int = Field(5, ge=1, le=25)
    earliest_year: int | None = Field(None, description="Filter out papers before this year")

    @field_validator("earliest_year")
    @classmethod
    def _check_year(cls, v):
        if v and not (1991 <= v <= datetime.now().year):
            raise ValueError("earliest_year must be between 1991 and current year")
        return v

def _search_arxiv(query: str, max_results: int = 5, earliest_year: int | None = None) -> str:
    client = arxiv.Client(page_size=max_results, delay_seconds=3, num_retries=2)  # respect arXiv rate limits
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    rows = []
    for r in client.results(search):
        yr = r.published.year if r.published else None
        if earliest_year and yr and yr < earliest_year:
            continue
        rows.append(
            f"- {r.title} ({yr if yr else ''}) — {', '.join(a.name for a in r.authors)}\n"
            f"  PDF: {r.pdf_url or ''}\n  Abs: {r.entry_id}\n  Summary: {r.summary.strip()[:500]}..."
        )
    return "\n".join(rows) if rows else "No matching arXiv papers."

arxiv_search = StructuredTool.from_function(
    func=_search_arxiv,
    name="arxiv_search",
    description="Search arXiv and return titles, authors, year, and links.",
    args_schema=ArxivSearchArgs,
    return_direct=False,
)
