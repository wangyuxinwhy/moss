from typing import Any, Dict

from serpapi import GoogleSearch
from trafilatura import extract, fetch_url


def search(q: str, engine: str = 'google') -> Dict[str, Any]:
    """Searches the web for the given query. use serpapi, serpapi 支持的 engine 都可以使用"""
    params = {
        "engine": engine,
        "q": q,
        "api_key": "007520dcbef059f3d21d6fd1b5eeadc9eeb7ca24fbbf5be4da28d6b073a01492"
    }

    # Perform the search
    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract the search results
    search_results = results.get('organic_results', [])

    # Return the top search results
    search_results[:5]  # Return the top 5 results
    return search_results


def extract_webpage_content(url: str) -> str:
    """fecth url and extract information from HTML, use trafilatura"""
    downloaded = fetch_url(url)
    # extract information from HTML
    result = extract(downloaded)
    return result or 'extract failed'


__all__ = ['search', 'extract_webpage_content']
