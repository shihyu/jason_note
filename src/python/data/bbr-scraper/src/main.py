import subprocess
import json
import time
import sys
import os
from bs4 import BeautifulSoup

def run_agent_command(command):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command '{command}': {e}", file=sys.stderr)
        return None

def get_article_links(page=1):
    print(f"Fetching article list for page {page}...", file=sys.stderr)
    url = f"https://www.bbr.com/articles/all?pageSize=24&page={page}"
    run_agent_command(f"agent-browser open '{url}'")
    time.sleep(8)
    run_agent_command("agent-browser scroll down 3000")
    time.sleep(3)
    
    output = run_agent_command("agent-browser snapshot -i --json")
    if not output:
        return []
        
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from snapshot on page {page}", file=sys.stderr)
        return []
        
    refs = data.get("data", {}).get("refs", {})
    
    candidate_refs = []
    for ref, details in refs.items():
        role = details.get("role")
        name = details.get("name", "")
        if role == "link" and any(cat in name for cat in [" Wine ", " Spirits ", " Guides ", " Collecting "]):
            candidate_refs.append(ref)
            
    print(f"Found {len(candidate_refs)} candidate links. Checking URLs...", file=sys.stderr)
    
    article_urls = []
    for ref in candidate_refs:
        href_json = run_agent_command(f"agent-browser get attr @{ref} href --json")
        try:
            res = json.loads(href_json)
            href = res.get("data", {}).get("value")
            if href and "/articles/" in href and href != "/articles/all":
                full_url = href if href.startswith("http") else f"https://www.bbr.com{href}"
                full_url = full_url.split('?')[0]
                if full_url not in article_urls:
                    article_urls.append(full_url)
        except:
            continue
            
    return article_urls

def scrape_article(url):
    print(f"Scraping {url}...", file=sys.stderr)
    run_agent_command(f"agent-browser open '{url}'")
    time.sleep(4)
    
    html = run_agent_command("agent-browser get html body")
    if not html:
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    
    article = {}
    article['url'] = url
    
    title_tag = soup.select_one('h1.sf-heading__title')
    article['title'] = title_tag.get_text(strip=True) if title_tag else ""
    
    date_tag = soup.select_one('.read-time')
    article['date'] = date_tag.get_text(strip=True) if date_tag else ""
    
    author_tag = soup.select_one('.author-information--name')
    article['author'] = author_tag.get_text(strip=True) if author_tag else ""
    
    content_div = soup.select_one('.rich-text-body-markdown') or soup.select_one('.rich-text-body')
    if content_div:
        article['content'] = content_div.get_text("\n\n", strip=True)
    else:
        article['content'] = ""
        
    return article

def main():
    all_articles = []
    seen_urls = set()
    
    # User can adjust the page limit. Setting to 2 for a reasonable run.
    MAX_PAGES = 2 
    
    for page in range(1, MAX_PAGES + 1):
        urls = get_article_links(page)
        if not urls:
            print(f"No articles found on page {page}. Stopping.", file=sys.stderr)
            break
            
        print(f"Processing {len(urls)} articles from page {page}...", file=sys.stderr)
        for url in urls:
            if url in seen_urls:
                continue
            
            try:
                data = scrape_article(url)
                if data and data['title']:
                    all_articles.append(data)
                    seen_urls.add(url)
            except Exception as e:
                print(f"Error scraping {url}: {e}", file=sys.stderr)
        
        # Small delay between pages
        time.sleep(2)
            
    # Output result to stdout for redirection to file
    print(json.dumps(all_articles, indent=2, ensure_ascii=False))
    print(f"Finished. Total articles scraped: {len(all_articles)}", file=sys.stderr)

if __name__ == "__main__":
    main()