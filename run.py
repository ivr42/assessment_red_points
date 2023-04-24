from src.github_crawler import GitHubCrawler

if __name__ == "__main__":
    test_inputs = [
        """
        {
          "keywords": [
            "openstack",
            "nova",
            "css"
          ],
          "proxies": [
            "113.53.231.133:3129",
            "20.121.242.93:3128",
            "46.101.13.77:80"
          ],
          "type": "Wikis"
        }
        """,
        {
            "keywords": ["python", "django-rest-framework", "jwt"],
            "proxies": [
                "113.53.231.133:3129",
                "20.121.242.93:3128",
                "46.101.13.77:80",
            ],
            "type": "Repositories",
        },
    ]

    crawler = GitHubCrawler(test_inputs[1])
    crawler.crawl()
    output = crawler.json(indent=1)
    print(output)
