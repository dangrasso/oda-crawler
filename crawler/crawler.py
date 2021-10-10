import random
from abc import ABC, abstractmethod
from time import sleep
from typing import Optional

import requests
from bs4 import BeautifulSoup

from crawler.frontier import Frontier, InMemorySetFrontier
from crawler.util import get_base_url, to_absolute_url


class Crawler(ABC):

    def __init__(self, url: str, max_visits: int, frontier: Frontier = None, visited: set[str] = None):
        if frontier is None:
            frontier = InMemorySetFrontier()
        if visited is None:
            visited = set()
        self.frontier = frontier
        self.visited = visited  # IDEA: abstract away the cache of visited pages, to support a shared cache middleware
        self.max_visits = max_visits
        frontier.enqueue_next([url])

    @abstractmethod
    def should_visit(self, url: str) -> bool:
        """Predicate: should the url be visited?"""
        pass

    @abstractmethod
    def should_prioritize_visit(self, url: str) -> bool:
        """Predicate: should the url be visited before all others?"""
        pass

    @abstractmethod
    def should_collect(self, url: str, status_code: int) -> bool:
        """Predicate: should the url be collected?"""
        pass

    @abstractmethod
    def collect(self, url: str, html: Optional[BeautifulSoup], status_code: int) -> None:
        """
        Consumer: defines the logic for collecting the content of a page.
        It is only invoked on pages with urls satisfying the should_collect() predicate.
        """
        pass

    def fetch_content(self, url: str, retries: int = 3) -> tuple[Optional[BeautifulSoup], int]:
        res = requests.get(url)
        # delay after each fetch, to avoid flooding the server
        sleep(round(random.uniform(0.5, 1.5), 1))

        if res.ok:
            html = BeautifulSoup(res.content, "html.parser")
            return (html, res.status_code)

        print(f"Got {res.status_code} response for '{url}'")

        if retries > 0 and res.status_code == 429:  # <- Too Many Requests
            sleep(res.headers.get("Retry-After", 60))
            self.fetch_content(url, retries - 1)

        return (None, res.status_code)

    def parse_links(self, url: str, html: Optional[BeautifulSoup]) -> set[str]:
        if html is None:
            return set()

        anchors = html.find_all("a")
        base_url = get_base_url(url)
        urls = {to_absolute_url(base_url, a.attrs['href']) for a in anchors if 'href' in a.attrs}
        return urls

    def visit(self, url: str):
        self.visited.add(url)
        print(f"[v:{len(self.visited)}|f:{len(self.frontier)}] Visiting: {url}")
        (content, status_code) = self.fetch_content(url)

        if content is not None:
            new_urls = {u for u in self.parse_links(url, content) if self.should_visit(u) and u not in self.visited}
            self.expand_frontier(new_urls)

        if self.should_collect(url, status_code):
            self.collect(url, content, status_code)

    def expand_frontier(self, new_urls: set[str]):
        visit_first = []
        visit_later = []
        for u in new_urls:
            if self.should_prioritize_visit(u):
                visit_first.append(u)
            else:
                visit_later.append(u)

        self.frontier.enqueue_next(visit_first)
        self.frontier.enqueue_last(visit_later)

    def crawl(self):
        while len(self.frontier) > 0 and len(self.visited) < self.max_visits:
            next_url = self.frontier.pop()
            if next_url not in self.visited:
                self.visit(next_url)

    def print_stats(self):
        print(f"visited: {len(self.visited)} pages")
        print(f"frontier: {len(self.frontier)} pages")
