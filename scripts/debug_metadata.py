"""Debug para verificar estrutura HTML e metadados das páginas."""

from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper
from bs4 import BeautifulSoup

config = BrowserConfig(headless=True)

with ProfessionalScraper(config) as scraper:
    infomoney = InfoMoneyScraper(scraper)
    urls = infomoney.get_latest_articles(limit=1)
    
    if urls:
        url = urls[0]
        print(f"URL: {url}\n")
        
        scraper.get_page(url, wait_time=3)
        html = scraper.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        # Verificar meta tags de data
        print("=" * 70)
        print("META TAGS RELEVANTES:")
        print("=" * 70)
        
        date_metas = [
            'article:published_time',
            'datePublished',
            'date',
            'pubdate',
            'publish_date',
            'dc.date',
            'sailthru.date',
        ]
        
        for meta_name in date_metas:
            # Property
            tag = soup.find('meta', {'property': meta_name})
            if tag:
                print(f"property={meta_name}: {tag.get('content')}")
            
            # Name
            tag = soup.find('meta', {'name': meta_name})
            if tag:
                print(f"name={meta_name}: {tag.get('content')}")
        
        # JSON-LD
        print("\n" + "=" * 70)
        print("JSON-LD:")
        print("=" * 70)
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for i, script in enumerate(scripts[:2]):  # Primeiros 2
            print(f"\nScript {i+1}:")
            print(script.string[:500] if script.string else "None")
        
        # time tags
        print("\n" + "=" * 70)
        print("TIME TAGS:")
        print("=" * 70)
        time_tags = soup.find_all('time')
        for time_tag in time_tags[:5]:
            print(f"datetime: {time_tag.get('datetime')}")
            print(f"text: {time_tag.get_text()}")
            print()
