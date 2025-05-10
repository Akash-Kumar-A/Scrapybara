# Install asyncio-compatible reactor BEFORE importing Scrapy's CrawlerProcess
import sys
import asyncio

# Fix for Windows/Anaconda: Use asyncio reactor
from twisted.internet import asyncioreactor
try:
    asyncioreactor.install()
except Exception:
    pass

import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser


class TextExtractorSpider(scrapy.Spider):
    name = "text_extractor"

    def __init__(self, url=None, *args, **kwargs):
        super(TextExtractorSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "header", "footer", "nav", "form"]):
            tag.decompose()

        text = "\n".join(line.strip() for line in soup.get_text().splitlines() if line.strip())
        self.logger.info("\nExtracted Textual Content:\n" + text)
        print("\nExtracted Textual Content:\n" + text)


def check_robots_txt(url):
    try:
        robots_url = f"{url.rsplit('/', 1)[0]}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        print(f"Error checking robots.txt: {e}")
        return True


def main():
    url = input("Enter the URL to scrape (e.g., https://example.com): ").strip()

    if not url.startswith(("http://", "https://")):
        print("Invalid URL. Please include http:// or https://")
        sys.exit(1)

    if not check_robots_txt(url):
        print("Scraping is disallowed by robots.txt. Please respect the website's terms.")
        sys.exit(1)

    print("Extracting textual content using Scrapy...")
    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/5.0",
        "ROBOTSTXT_OBEY": True,
        "LOG_LEVEL": "ERROR"
    })
    process.crawl(TextExtractorSpider, url=url)
    process.start()


if __name__ == "__main__":
    main()
