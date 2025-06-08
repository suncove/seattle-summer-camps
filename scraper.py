import requests
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='camp_scraper.log'
)

class CampScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Load camp sources
        try:
            with open('data/camp_sources.json', 'r') as f:
                self.sources = json.load(f)['sources']
        except FileNotFoundError:
            logging.error("camp_sources.json not found")
            self.sources = []

    def scrape_site(self, url: str) -> List[Dict]:
        """Scrape a specific website for camp information"""
        try:
            logging.info(f"Starting to scrape: {url}")
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            camps = self.extract_camp_data(soup, url)
            logging.info(f"Found {len(camps)} camps at {url}")
            return camps
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return []

    def extract_camp_data(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract camp information from HTML based on the site"""
        # Return demo data
        return [
            {
                "name": "STEM Discovery Camp",
                "provider": "Pacific Science Center",
                "ages": "8-12",
                "dates": ["2025-07-10", "2025-07-24"],
                "cost": 475.0,
                "location": "200 2nd Ave N, Seattle",
                "description": "Hands-on STEM exploration for curious minds"
            },
            {
                "name": "Zoo Explorers",
                "provider": "Woodland Park Zoo",
                "ages": "7-11",
                "dates": ["2025-07-17"],
                "cost": 425.0,
                "location": "5500 Phinney Ave N, Seattle",
                "description": "Discover wildlife and conservation"
            },
            {
                "name": "Youth Kayaking",
                "provider": "Moss Bay",
                "ages": "10-13",
                "dates": ["2025-07-08", "2025-07-22"],
                "cost": 495.0,
                "location": "1001 Fairview Ave N, Seattle",
                "description": "Adventure on Seattle's waters"
            }
        ]

    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all sources defined in camp_sources.json"""
        all_camps = []
        for source in self.sources:
            try:
                logging.info(f"Scraping {source['name']}")
                camps = self.scrape_site(source['url'])
                all_camps.extend(camps)
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {str(e)}")
        return all_camps
