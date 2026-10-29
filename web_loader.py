"""
Web Page & URL Loader
Scrapes web pages, extracts main content, cleans HTML boilerplate,
and creates cited chunks for external research intelligence.
"""

import re
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup


class WebChunk:
    """Represents a text chunk from a web page."""
    def __init__(self, url: str, title: str, section: str, text: str):
        self.url = url
        self.title = title
        self.section = section
        self.text = text

    @property
    def citation(self) -> str:
        return f"[Source: {self.title} | {self.url}]"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "section": self.section,
            "text": self.text,
            "citation": self.citation
        }


class WebLoader:
    """Fetches and cleans web pages."""

    @staticmethod
    def load(url: str, chunk_size: int = 800, overlap: int = 100) -> List[WebChunk]:
        """Scrape URL and return text chunks."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EnterpriseResearchBot/1.0"
        }
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise RuntimeError(f"Failed to fetch URL {url}: {e}")

        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else url

        # Remove scripts, styles, navigations, footers
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]):
            tag.decompose()

        # Find main content container if available
        main = soup.find("main") or soup.find("article") or soup.find("div", {"id": re.compile(r"content|main", re.I)}) or soup.body
        if not main:
            main = soup

        # Extract text by paragraphs and headings
        blocks = []
        current_section = "Overview"

        for elem in main.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            text = elem.get_text().strip()
            if not text:
                continue
            if elem.name in ["h1", "h2", "h3", "h4"]:
                current_section = text
            else:
                blocks.append((current_section, text))

        if not blocks:
            # Fallback to general text
            all_text = soup.get_text(separator="\n", strip=True)
            paragraphs = [p.strip() for p in all_text.split("\n") if len(p.strip()) > 30]
            blocks = [("Page Content", p) for p in paragraphs]

        chunks = []
        current_chunk_text = []
        curr_len = 0
        active_sec = "Overview"

        for sec, text in blocks:
            if curr_len + len(text) > chunk_size and current_chunk_text:
                full_text = "\n".join(current_chunk_text)
                chunks.append(WebChunk(url=url, title=title, section=active_sec, text=full_text))
                # Retain last piece for overlap
                current_chunk_text = [text]
                curr_len = len(text)
                active_sec = sec
            else:
                current_chunk_text.append(text)
                curr_len += len(text)
                active_sec = sec

        if current_chunk_text:
            chunks.append(WebChunk(url=url, title=title, section=active_sec, text="\n".join(current_chunk_text)))

        return chunks
