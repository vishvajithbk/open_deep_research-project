# smoke_arxiv_tool.py
from open_deep_research.arxiv_tool import _search_arxiv

if __name__ == "__main__":
    print("Querying arXiv…")
    out = _search_arxiv(query='vision transformer', 
                        max_results=2, 
                        earliest_year=2023)

    print(out)
