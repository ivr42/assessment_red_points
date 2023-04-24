from __future__ import annotations

from abc import ABC, abstractmethod
from io import StringIO
from typing import TYPE_CHECKING
from urllib.parse import urlunparse

from lxml import etree

from src.data_model import URL, Extra, Result

if TYPE_CHECKING:
    import aiohttp


class Task(ABC):
    """Abstract base class that defines the structure of a web scraping task.

    Subclasses of Task must implement the `extract_info` method, which takes
    the HTML content of the response as input and returns an extracted
    information.

    Attributes:
    url (URL): The URL to scrape.
    proxy (str, optional): The proxy to use for the HTTP request, if any.
    session (aiohttp.ClientSession, optional):
        The aiohttp session object to use for the HTTP request.
    """


    def __init__(
        self,
        url: URL,
        proxy: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        self.url = url
        self.proxy = proxy
        self.session = session

    async def do_task(self):
        """
        Performs the web scraping task.

        This method sends an HTTP GET request to the URL specified in
        `self.url`, using the session and proxy specified in the instance
        attributes. It then extracts information from the HTML content of the
        response using the `extract_info` method.

        Returns:
            An extracted information.
        """

        if self.session is None:
            return {}
        async with self.session.get(
            self.url.url, proxy=self.proxy
        ) as response:
            html_data = await response.text()
            return self.extract_info(html_data)

    @abstractmethod
    def extract_info(self, html_data: str):
        pass


class SearchTask(Task):
    """Performs a search on GitHub and extracts URLs of search results.

    This class inherits from the Task class and implements the `extract_info`
    method to extract URLs of search results from the HTML content of the
    search response.

    Attributes:
    XPATH (str):
        The XPath expression to use for extracting URLs of search results.
    """

    XPATH = r"/html/body//main//a[@data-hydro-click]"

    @staticmethod
    def make_page_url(path: str) -> str:
        return urlunparse(("https", "github.com", path, "", "", ""))

    def extract_info(self, html_data: str):
        result = []

        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html_data), parser)
        for child in tree.xpath(self.XPATH):
            url = self.make_page_url(child.attrib["href"])
            result.append(Result(url))

        return result


class GetExtraTask(Task):
    """Performs a search extra information on GitHub.

    This class inherits from the Task class and implements the `extract_info`
    method to extract extra information.

    Attributes:
    LANGUAGE_STAT_XPATH (str):
        The XPath expression to use for extracting language statistics.
    OWNER_XPATH (str):
        The XPath expression to use for extracting repo's owner information.
    """
    LANGUAGE_STAT_XPATH = (
        r'/html/body//main//a[@data-ga-click="Repository, '
        'language stats search click, location:repo overview"]/span'
    )
    OWNER_XPATH = r'/html/body//main//span[@itemprop="author"]/a'

    @staticmethod
    def pairwise(iterable):
        a = iter(iterable)
        return zip(a, a)

    def extract_info(self, html_data: str):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html_data), parser)

        language_stats_list = [
            child.text for child in tree.xpath(self.LANGUAGE_STAT_XPATH)
        ]
        language_stats = dict(self.pairwise(language_stats_list))

        owner_list = tree.xpath(self.OWNER_XPATH)
        owner = None
        if owner_list:
            owner = owner_list[0].text.strip()

        extra = Extra(owner=owner, language_stats=language_stats)

        return extra
