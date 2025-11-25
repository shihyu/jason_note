import requests
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_hacker_news(url):
    """
    Scrapes Hacker News page and extracts news title, URL, and score.

    Args:
        url (str): The URL of the Hacker News page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a news item.
              Returns an empty list if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = []

        athing_rows = soup.find_all('tr', class_='athing')

        for row in athing_rows:
            title_element = row.find('a', class_='titlelink')
            if not title_element:
                title_element = row.find('span', class_='titleline').find('a')
                if not title_element:
                    logging.warning("Title element not found, skipping row.")
                    continue
            
            title = title_element.text.replace('\n', ' ').strip()
            url = title_element['href']

            score_element = row.find_next_sibling('tr').find('span', class_='score')
            score = int(score_element.text.split()[0]) if score_element else None

            news_items.append({
                'title': title,
                'url': url,
                'score': score
            })

        return news_items

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

def main():
    """
    Scrapes multiple Hacker News pages and saves the combined data to a JSON file.
    """
    urls = [
        'https://news.ycombinator.com/',
        'https://news.ycombinator.com/?p=2',
        'https://news.ycombinator.com/?p=3'
    ]
    all_news = []

    for url in urls:
        logging.info(f"Scraping {url}")
        news = scrape_hacker_news(url)
        if news:
            all_news.extend(news)
        else:
            logging.warning(f"Failed to scrape {url}")

    try:
        with open('Hacker_news2.json', 'w', encoding='utf-8') as f:
            json.dump(all_news, f, indent=4, ensure_ascii=False)
        logging.info("Data saved to Hacker_news2.json")
    except Exception as e:
        logging.error(f"Failed to save to JSON: {e}")

if __name__ == "__main__":
    main()