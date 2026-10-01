import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


visited = set()
MAX_PAGES = 3000


def web_crawler(unique_urls):
    """Crawl web pages and save their HTML content locally."""

    while unique_urls and len(visited) < MAX_PAGES:

        print(f"Unique links: {len(unique_urls)}")
        print(f"Visited links: {len(visited)}")

        current_url = unique_urls.pop()

        if current_url in visited:
            continue

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; "
                    "rv:77.0) Gecko/20100101 Firefox/77.0"
                )
            }

            response = requests.get(
                current_url,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.content,
                "html.parser"
            )

            save_page(response, soup)

            visited.add(current_url)

            for node in soup.find_all("a", href=True):
                href = node.get("href")
                full_url = urljoin(current_url, href)

                if urlparse(full_url).scheme not in (
                    "http",
                    "https"
                ):
                    continue

                if (
                    full_url not in visited
                    and full_url not in unique_urls
                ):
                    unique_urls.add(full_url)

            time.sleep(1)

        except requests.RequestException as error:
            print(f"Request failed: {current_url}")
            print(f"Error: {error}")
            visited.add(current_url)

        except Exception as error:
            print(f"Error processing {current_url}: {error}")
            visited.add(current_url)


def save_page(page, soup):
    """Save the scraped HTML page to the storage directory."""

    storage_directory = os.path.expanduser("~/storage")

    os.makedirs(
        storage_directory,
        exist_ok=True
    )

    try:
        title = soup.title.string if soup.title else "untitled"

        safe_title = "".join(
            character
            for character in title
            if character.isalnum()
            or character in (" ", "-", "_")
        ).strip()

        if not safe_title:
            safe_title = "untitled"

        filename = f"html_{safe_title}.html"

        file_path = os.path.join(
            storage_directory,
            filename
        )

        print(f"Saving: {file_path}")

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(page.text)

    except OSError as error:
        print(f"Unable to save page: {error}")


def main():
    """Start the web crawler."""

    base_url = input(
        "Enter URL to start scraping website:\n"
    ).strip()

    if not base_url.startswith(
        ("http://", "https://")
    ):
        print(
            "Please enter a valid URL starting with "
            "http:// or https://"
        )
        return

    unique_urls = {base_url}

    web_crawler(unique_urls)

    print("\nCrawling completed.")
    print(f"Total pages visited: {len(visited)}")


if __name__ == "__main__":
    main()
