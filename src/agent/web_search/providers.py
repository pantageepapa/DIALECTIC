"""
Web search provider abstractions supporting Brave Search and Perplexity Sonar.

Both providers expose the same string-based output contract that the rest of the
agent relies on (`Search Results for: <query> ...`). This keeps downstream
processing unchanged while allowing us to swap implementations via an
environment toggle.
"""

from __future__ import annotations

import importlib
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

DEFAULT_RESULT_COUNT = 3
DEFAULT_COUNTRY = "US"
DEFAULT_MAX_TOKENS_PER_PAGE = 200


class WebSearchProvider(ABC):
    """Minimal interface for search providers."""

    @abstractmethod
    def search(self, query: str) -> str:
        """Execute a query and return a formatted string."""


class BraveSearchProvider(WebSearchProvider):
    """Wrapper around LangChain's BraveSearch tool."""

    def __init__(self, search_end_date: str, *, country: str = DEFAULT_COUNTRY):
        try:
            BraveSearch = importlib.import_module(
                "langchain_community.tools.brave_search.tool"
            ).BraveSearch
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                "langchain_community.tools.brave_search.tool.BraveSearch is required for BraveSearchProvider."
            ) from exc

        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY environment variable is required")

        freshness = self._convert_date_to_freshness(search_end_date)
        self._brave_search = BraveSearch.from_api_key(
            api_key=api_key,
            search_kwargs={
                "count": DEFAULT_RESULT_COUNT,
                "country": country,
                "search_lang": "en",
                "safesearch": "moderate",
                "freshness": freshness,
                "result_filter": "web,news",
            },
        )

    def search(self, query: str) -> str:
        return self._brave_search.run(query)

    @staticmethod
    def _convert_date_to_freshness(search_end_date: str) -> str:
        if "T" in search_end_date:
            end_date = datetime.fromisoformat(search_end_date.replace("Z", "+00:00"))
        else:
            end_date = datetime.strptime(search_end_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=365)
        return f"{start_date.strftime('%Y-%m-%d')}to{end_date.strftime('%Y-%m-%d')}"


class SonarSearchProvider(WebSearchProvider):
    """Client for Perplexity Sonar Search API."""

    BASE_URL = "https://api.perplexity.ai/search"

    def __init__(
        self,
        search_end_date: str,
        *,
        country: str = DEFAULT_COUNTRY,
        max_results: int = DEFAULT_RESULT_COUNT,
        max_tokens_per_page: int = DEFAULT_MAX_TOKENS_PER_PAGE,
    ):
        api_key = os.getenv("PPLX_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError(
                "Perplexity Sonar requires PPLX_API_KEY (or PERPLEXITY_API_KEY) environment variable."
            )

        self._api_key = api_key
        self._country = country
        self._max_results = max(1, min(max_results, 20))
        self._max_tokens_per_page = max_tokens_per_page
        self._search_after, self._search_before = self._derive_date_filters(search_end_date)
        try:
            self._requests = importlib.import_module("requests")
        except ImportError as exc:
            raise ImportError(
                "The 'requests' package is required for SonarSearchProvider."
            ) from exc

    def search(self, query: str) -> str:
        payload = {
            "query": query,
            "max_results": self._max_results,
            "country": self._country,
            "max_tokens_per_page": self._max_tokens_per_page,
        }

        if self._search_after:
            payload["search_after_date_filter"] = self._search_after
        if self._search_before:
            payload["search_before_date_filter"] = self._search_before

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._requests.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not isinstance(results, list):
                    raise ValueError("Unexpected Sonar response format: 'results' is not a list")

                return self._format_results(query, results)

            except self._requests.exceptions.HTTPError as e:
                # Check if it's a rate limit error (429) or server error (5xx)
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    # Retry on rate limit or server errors
                    if status_code in (429, 500, 502, 503, 504):
                        if attempt < max_retries - 1:
                            # Exponential backoff: 1s, 2s, 4s
                            wait_time = 2 ** attempt
                            time.sleep(wait_time)
                            continue
                # Re-raise if not retryable or last attempt
                raise
            except (self._requests.exceptions.Timeout, self._requests.exceptions.ConnectionError) as e:
                # Retry on timeout or connection errors
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                raise

        # This should not be reached, but just in case
        raise RuntimeError(f"Failed to complete search after {max_retries} attempts")

    @staticmethod
    def _derive_date_filters(search_end_date: str) -> tuple[Optional[str], Optional[str]]:
        """Return (after, before) tuple formatted as MM/DD/YYYY."""
        if not search_end_date:
            return None, None

        if "T" in search_end_date:
            end = datetime.fromisoformat(search_end_date.replace("Z", "+00:00"))
        else:
            end = datetime.strptime(search_end_date, "%Y-%m-%d")

        start = end - timedelta(days=365)
        return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")

    @staticmethod
    def _format_results(query: str, results: List[dict]) -> str:
        lines: List[str] = [f"Search Results for: {query}", ""]

        if not results:
            lines.append("No search results returned.")
            return "\n".join(lines)

        for index, item in enumerate(results, start=1):
            title = item.get("title") or "No title"
            url = item.get("url") or "No URL provided"
            snippet = item.get("snippet") or ""
            date = item.get("date")

            lines.append(f"{index}. {title} — {url}")
            if snippet:
                lines.append(f"   {snippet}")
            lines.append("")

        return "\n".join(lines).rstrip()


def get_provider(search_end_date: str, *, provider_name: str) -> WebSearchProvider:
    """Factory to instantiate the requested provider."""
    provider = provider_name.lower()
    if provider == "sonar":
        return SonarSearchProvider(search_end_date=search_end_date)
    if provider == "brave":
        return BraveSearchProvider(search_end_date=search_end_date)
    raise ValueError(f"Unsupported web search provider '{provider_name}'.")


