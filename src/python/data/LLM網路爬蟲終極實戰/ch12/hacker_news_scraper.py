import requests
from bs4 import BeautifulSoup
import json

def scrape_hacker_news():
    url = "https://news.ycombinator.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    news_list = []
    
    table = soup.find('table', id='hnmain')
    rows = table.find_all('tr')

    for i in range(0, len(rows) - 2, 3):
        title_row = rows[i]
        score_row = rows[i+1]

        title_element = title_row.find('a', class_='storylink')
        if title_element:
            title = title_element.text
            url = title_element['href']

            score_element = score_row.find('span', class_='score')
            score = int(score_element.text.split()[0]) if score_element else 0

            news_item = {
                'title': title,
                'url': url,
                'score': score
            }
            news_list.append(news_item)

    return news_list

def save_to_json(data, filename='news2.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    news_data = scrape_hacker_news()
    save_to_json(news_data)

if __name__ == "__main__":
    main()