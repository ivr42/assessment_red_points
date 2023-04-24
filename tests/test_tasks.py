from unittest.mock import AsyncMock

import aiohttp
import pytest

from src.data_model import URL, Extra, Result
from src.task import GetExtraTask, SearchTask


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


def test_search_task_extract_info():
    url = URL("https://github.com")
    html_data = """
        <html>
            <body>
                <main>
                    <a href="/path1" data-hydro-click></a>
                    <a href="/path2" data-hydro-click></a>
                    <a href="/path3" data-hydro-click></a>
                </main>
            </body>
        </html>
    """
    expected_results = [
        Result("https://github.com/path1"),
        Result("https://github.com/path2"),
        Result("https://github.com/path3"),
    ]

    search_task = SearchTask(url)
    results = search_task.extract_info(html_data)

    assert results == expected_results


def test_get_extra_task_extract_info():
    html_data = """
        <html>
            <body>
                <main>
                    <span itemprop="author"><a>owner_name</a></span>
                    <a data-ga-click="Repository, language stats search click, location:repo overview">
                        <span>Python</span>
                        <span>98.77%</span>
                        <span>JavaScript</span>
                        <span>1.23%</span>
                    </a>
                </main>
            </body>
        </html>
    """
    expected_extra = Extra(
        owner="owner_name",
        language_stats={
            "Python": "98.77%",
            "JavaScript": "1.23%",
        },
    )

    get_extra_task = GetExtraTask(Result("https://github.com"))
    extra = get_extra_task.extract_info(html_data)

    assert extra == expected_extra


@pytest.mark.asyncio
async def test_search_task_do_task_no_session():
    url = URL("https://github.com")
    search_task = SearchTask(url)
    results = await search_task.do_task()

    assert results == {}


@pytest.mark.asyncio
async def test_search_task_do_task():
    url = URL("https://github.com")
    html_data = """
        <html>
            <body>
                <main>
                    <a href="/path1" data-hydro-click></a>
                    <a href="/path2" data-hydro-click></a>
                    <a href="/path3" data-hydro-click></a>
                </main>
            </body>
        </html>
    """
    expected_results = [
        Result("https://github.com/path1"),
        Result("https://github.com/path2"),
        Result("https://github.com/path3"),
    ]

    session_mock = AsyncMock(aiohttp.ClientSession)
    session_mock.get.return_value.__aenter__.return_value.text.return_value = (
        html_data
    )

    search_task = SearchTask(url, session=session_mock)
    results = await search_task.do_task()

    assert results == expected_results
