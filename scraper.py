import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_kcomwel_standards():
    """
    Scrapes the latest Industrial Accident Compensation standards from KCOMWEL.
    Since the site structure often changes, this includes robust fallbacks.
    """
    # Baseline 2026 values (verified via official 2025-84 notice)
    data = {
        "year": 2026,
        "max_daily_wage": 268299,
        "min_daily_wage": 82560,
        "update_date": str(datetime.date.today()),
        "source": "Manual Verification (Notice 2025-84)"
    }

    # Attempt to scrape from the 'Standards' page (often base.jsp or similar)
    urls = [
        "https://www.comwel.or.kr/comwel/paym/paym/base.jsp",
        "https://www.comwel.or.kr/comwel/comp/rewd/unjo04.jsp"
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Regex for Max/Min values in the format '268,299' or '268299'
                # Looking for context like '최고' and '보상한도'
                max_match = re.search(r'최고\s?보상한도액[^0-9]*([\d,]+)', text)
                min_match = re.search(r'최저\s?보상한도액[^0-9]*([\d,]+)', text)
                
                if max_match and min_match:
                    data["max_daily_wage"] = int(max_match.group(1).replace(',', ''))
                    data["min_daily_wage"] = int(min_match.group(1).replace(',', ''))
                    data["source"] = f"Scraped from {url}"
                    break
        except Exception as e:
            print(f"Scraping error for {url}: {e}")

    # Save to standards.json
    with open('standards.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Updated standards: {data}")

if __name__ == "__main__":
    scrape_kcomwel_standards()
