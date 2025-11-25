import requests
from bs4 import BeautifulSoup
import csv, re

URL = "http://books.toscrape.com/index.html"
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
           "AppleWebKit/537.36 (KHTML, like Gecko)"
           "Chrome/63.0.3239.132 Safari/537.36"}

def get_text(tag):
    return tag.text.strip() if tag else "N/A"

def get_attrib(tag, attrib):
    return tag[attrib].strip() if tag else "N/A"
    
def extract_price(price_text):
    if price_text == "N/A":
        return "N/A"
    price_match = re.search(r'[\d.]+', price_text)
    if price_match:
        return price_match.group()
    else:
        return "N/A"    
    
books = [["圖書封面","圖書名稱","圖書連結","圖書價格"]]
r = requests.get(URL, headers=headers)
if r.status_code == requests.codes.ok:
    soup = BeautifulSoup(r.text, 'lxml')
    tag_ul = soup.find("ol", class_="row")
    rows = tag_ul.find_all("li")  # 或find_all("article")
    for row in rows:
        cover_div = row.find("div",class_="image_container")
        img_url = get_attrib(cover_div.img, "src")
        name_h3 = get_attrib(row.find("h3").a, "title")
        book_url = get_attrib(row.find("h3").a, "href")
        price_div = get_text(row.find("div",
                             class_="product_price").p)
        price = extract_price(price_div)       
        book= [img_url, name_h3, book_url, price]
        # print(book)
        books.append(book)
    
    with open("books.csv", "w+", newline="",
              encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        for item in books:
            writer.writerow(item)        
    print("寫入CSV檔案: books.csv")    
else:
    print("HTTP請求錯誤...")