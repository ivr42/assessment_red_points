# GitHub Crawler
(Python developer position technical task)

The task itself you can find here: 
https://confluence.rdpnts.com/display/IKB/Python+developer+technical+task

## Utilizes
- python 3.10
- aiohttp 3.8.4 (to make requests to GitHub.com)
- lxml 4.9.2 (for parsing HTTP documents)

For testing, I use:
- pytest 7.3.1
- pytest-asyncio 0.21.0
- coverage 7.2.3 (to ensure, that I have enough tests)

## Install
```shell
git pull https://github.com/ivr42/assessment_red_points
cd assessment_red_points
python -m venv .venv
. .venv/bin/activate
pip install -r requrements.txt
```

## Use

Import crawler: 
```python
from src.github_crawler import GitHubCrawler
```

Generate input data:
```json
{
    "keywords": ["python", "django-rest-framework", "jwt"],
    "proxies": [
        "113.53.231.133:3129",
        "20.121.242.93:3128",
        "46.101.13.77:80",
    ],
    "type": "Repositories",
}
```
You can use it as `str` with JSON or as a Python structure that represents
this JSON.

Create the Crawler object
```python
crawler = GitHubCrawler(input_data)
```
Crawl the crawler
```python
crawler.crawl()
```

Get the results

```python
output = crawler.json(indent=1)
print(output)
```

## Coverage with unit tests
```
(.venv) $ coverage run -m pytest
================================= test session starts ==================================
platform darwin -- Python 3.10.9, pytest-7.3.1, pluggy-1.0.0 -- /Users/ivr/Git/assessment_red_points/.venv/bin/python
rootdir: /Users/ivr/Git/assessment_red_points
configfile: pytest.ini
testpaths: tests/
plugins: asyncio-0.21.0
asyncio: mode=strict
collected 4 items

tests/test_tasks.py::test_search_task_extract_info PASSED                        [ 25%]
tests/test_tasks.py::test_get_extra_task_extract_info PASSED                     [ 50%]
tests/test_tasks.py::test_search_task_do_task_no_session PASSED                  [ 75%]
tests/test_tasks.py::test_search_task_do_task PASSED                             [100%]

================================== 4 passed in 0.25s ===================================
(.venv) $ coverage report
Name                Stmts   Miss  Cover
---------------------------------------
src/__init__.py         0      0   100%
src/data_model.py      10      0   100%
src/task.py            54      2    96%
---------------------------------------
TOTAL                  64      2    97%
(.venv) $
```