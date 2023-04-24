import asyncio
import json
import random
from dataclasses import asdict
from typing import Any
from urllib.parse import urlencode, urlunparse

import aiohttp

from src.data_model import Result
from src.task import GetExtraTask, SearchTask


class GitHubCrawler:
    """A class for crawling data from GitHub.

    Attributes:
        PROXY_TYPE (str): The type of proxy to use (currently set to "http").
        GITHUB_QUERY_TYPE (dict[str, str]):
            A dictionary mapping query types to their GitHub API strings.
        HEADERS (dict):
            A dictionary of HTTP headers to send with requests to GitHub.
        WORKERS (int): The number of worker tasks to use for crawling.

        keywords (list[str]): The list of keywords from the given input JSON.
        proxies (list[str]): The list of a properly formatted proxy URLs
        query_type (str): Query type from the given input JSON.
            (Repositories, Issues, and Wikis are supported)
    """

    PROXY_TYPE = "http"
    GITHUB_QUERY_TYPE = {
        "Repositories": "repositories",
        "Issues": "issues",
        "Wikis": "wikis",
    }
    HEADERS = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }
    WORKERS = 16

    def __init__(self, input_json: Any):
        """Initializes a new GitHubCrawler instance with the given input JSON.

        Arguments:
            input_json: String with JSON or the Python structure, represented
                this JSON.

        """
        self.keywords: list[str] = []
        self.proxies: list[str] = []
        self.query_type: str = ""
        self._result: list[Result] = []
        self._search_urls: list[str] = []
        self._task_queue: asyncio.Queue = asyncio.Queue()

        if type(input_json) == str:
            input_json = json.loads(input_json)

        self.keywords = input_json["keywords"]
        self.query_type = input_json["type"]
        self.proxies = [self.make_proxy_url(p) for p in input_json["proxies"]]

    def make_proxy_url(self, proxy):
        """Returns a properly formatted proxy URL from the given string."""
        return urlunparse((self.PROXY_TYPE, proxy, "", "", "", ""))

    def make_search_url(self, keyword: str) -> str:
        """Returns a search URL for the given keyword and query type."""
        query_params = {
            "q": keyword,
            "type": self.github_query_type,
        }
        return urlunparse(
            ("https", "github.com", "search", "", urlencode(query_params), "")
        )

    @property
    def random_proxy(self) -> str:
        """Returns a random proxy URL from the list of proxies."""
        random_index = random.randint(0, len(self.proxies) - 1)
        return self.proxies[random_index]

    @property
    def github_query_type(self) -> str:
        """Returns the GitHub API string for the current query type."""
        return self.GITHUB_QUERY_TYPE.get(self.query_type, "repositories")

    async def add_job(self):
        """Adds search tasks to the task queue for each keyword."""
        for keyword in self.keywords:
            url = self.make_search_url(keyword)
            task = SearchTask(Result(url))
            await self._task_queue.put(task)

    async def worker(self):
        """A worker task.

        Get tasks from the task queue and process them.
        Get data from processed tasks and add to the result attribute
        Add tasks gor getting extra data to the task queue.
        """
        async with aiohttp.ClientSession(headers=self.HEADERS) as s:
            while not self._task_queue.empty():
                task = await self._task_queue.get()
                task.session = s
                task.proxy = self.random_proxy
                results = await task.do_task()

                if type(task) == SearchTask:
                    self._result.extend(results)
                    for result in results:
                        extra_task = GetExtraTask(result, s)
                        await self._task_queue.put(extra_task)
                elif type(task) == GetExtraTask:
                    task.url.extra = results
                else:
                    continue

    async def async_crawl(self):
        """Run asynchronously the worker tasks."""
        workers = []

        await self.add_job()

        for _ in range(self.WORKERS):
            workers.append(asyncio.create_task(self.worker()))

        await asyncio.gather(*workers)

    def crawl(self):
        """Synchronous interface to the GitHubCrawler class

        Runs the async_crawl method synchronously using asyncio.run.
        """
        asyncio.run(self.async_crawl())

    def json(self, *args, **kwargs):
        """Returns a JSON string representation of the _result list."""
        return json.dumps([asdict(r) for r in self._result], *args, **kwargs)
