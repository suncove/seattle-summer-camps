import requests
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import aiohttp
import asyncio
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
import io
import time
import random

class SeattleCampScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.setup_logging()
        self.setup_selenium()
        self.cache = {}
        
    def setup_logging(self):
        logging.basicConfig(
            filename='camp_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    # Main source categories
    CAMP_SOURCES = {
        'community_centers': [
            'https://www.seattle.gov/parks/find/centers',
            'https://www.bellevuewa.gov/city-government/departments/parks/community-centers',
            # Add more community centers
        ],
        'museums': [
            'https://www.pacificsciencecenter.org/camps/',
            'https://www.mopop.org/programs-plus-education/',
            'https://www.seattleartmuseum.org/visit/calendar',
            'https://www.museumofflight.org/Education/Camps',
            # Add more museums
        ],
        'sports_facilities': [
            'https://www.seattleymca.org/programs/camp',
            'https://www.arena-sports.net/youth-programs',
            # Add more sports facilities
        ],
        'arts_organizations': [
            'https://www.sct.org/classes-camps/',
            'https://www.seattleopera.org/classes/',
            # Add more arts organizations
        ],
        'education_centers': [
            'https://www.idtech.com/locations/washington-summer-camps/seattle',
            'https://www.kumon.com/seattle-wa',
            # Add more education centers
        ],
        'outdoor_programs': [
            'https://www.mountaineers.org/youth',
            'https://www.rei.com/events/camping',
            # Add more outdoor programs
        ],
        'specialty_camps': [
            'https://www.codingwithkids.com/camp',
            'https://www.seattleaudubon.org/youth-programs/',
            # Add more specialty camps
        ]
    }

    async def scrape_all_sources(self) -> List[Dict]:
        """Scrape all camp sources concurrently"""
        all_camps = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for category, urls in self.CAMP_SOURCES.items():
                for url in urls:
                    tasks.append(self.scrape_source(session, url, category))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_camps.extend(result)
                else:
                    logging.error(f"Error during scraping: {str(result)}")
        
        return all_camps

    async def scrape_source(self, session: aiohttp.ClientSession, url: str, category: str) -> List[Dict]:
        """Scrape a single source using appropriate method"""
        try:
            # Check cache first
            if url in self.cache:
                return self.cache[url]

            if 'javascript' in await self.check_site_technology(url):
                return await self.scrape_javascript_site(url)
            elif '.pdf' in url:
                return await self.scrape_pdf(url)
            else:
                return await self.scrape_static_site(session, url, category)
        
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return []

    async def check_site_technology(self, url: str) -> List[str]:
        """Determine website technology"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    text = await response.text()
                    technologies = []
                    if 'react' in text.lower():
                        technologies.append('javascript')
                    if 'vue' in text.lower():
                        technologies.append('javascript')
                    if 'angular' in text.lower():
                        technologies.append('javascript')
                    return technologies
        except:
            return []

    async def scrape_javascript_site(self, url: str) -> List[Dict]:
        """Scrape sites that require JavaScript"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Allow dynamic content to load
            
            # Extract camp information
            camps = []
            camp_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='camp']")
            
            for element in camp_elements:
                camp = self.extract_camp_info_from_element(element)
                if camp:
                    camps.append(camp)
            
            return camps
        
        except Exception as e:
            logging.error(f"Error scraping JavaScript site {url}: {str(e)}")
            return []

    async def scrape_pdf(self, url: str) -> List[Dict]:
        """Extract camp information from PDF documents"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    pdf_content = await response.read()
                    pdf_file = io.BytesIO(pdf_content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    camps = []
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        camps.extend(self.extract_camps_from_text(text))
                    
                    return camps
        
        except Exception as e:
            logging.error(f"Error scraping PDF {url}: {str(e)}")
            return []

    async def scrape_static_site(self, session: aiohttp.ClientSession, url: str, category: str) -> List[Dict]:
        """Scrape regular HTML sites"""
        try:
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                camps = []
                # Look for common camp indicators
                camp_elements = soup.find_all(class_=re.compile(r'camp|program|class|event'))
                
                for element in camp_elements:
                    camp = self.extract_camp_info_from_element(element)
                    if camp:
                        camp['category'] = category
                        camps.append(camp)
                
                return camps
        
        except Exception as e:
            logging.error(f"Error scraping static site {url}: {str(e)}")
            return []

    def extract_camp_info_from_element(self, element) -> Optional[Dict]:
        """Extract structured camp information from HTML element"""
        try:
            # Try multiple patterns to find information
            name = self.find_camp_name(element)
            dates = self.find_dates(element)
            price = self.find_price(element)
            age_range = self.find_age_range(element)
            location = self.find_location(element)
            
            if name and dates:  # Minimum required information
                return {
                    'name': name,
                    'dates': dates,
                    'price': price,
                    'age_range': age_range,
                    'location': location,
                    'last_updated': datetime.now().isoformat()
                }
            return None
            
        except Exception as e:
            logging.error(f"Error extracting camp info: {str(e)}")
            return None

    def find_camp_name(self, element) -> Optional[str]:
        """Find camp name using multiple patterns"""
        patterns = [
            {'tag': 'h1', 'class': re.compile(r'title|name|heading')},
            {'tag': 'h2', 'class': re.compile(r'title|name|heading')},
            {'tag': 'h3', 'class': re.compile(r'title|name|heading')},
            {'tag': 'div', 'class': re.compile(r'title|name|heading')}
        ]
        
        for pattern in patterns:
            found = element.find(**pattern)
            if found:
                return found.text.strip()
        return None

    def find_dates(self, element) -> List[str]:
        """Extract dates using multiple patterns"""
        date_patterns = [
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:\s*-\s*\d{1,2})?,\s*202[0-9]',
            r'\d{1,2}/\d{1,2}/202[0-9]',
            r'202[0-9]-\d{2}-\d{2}'
        ]
        
        dates = []
        text = element.get_text()
        
        for pattern in date_patterns:
            found_dates = re.findall(pattern, text)
            dates.extend(found_dates)
        
        return self.standardize_dates(dates)

    def standardize_dates(self, dates: List[str]) -> List[str]:
        """Convert dates to standard format (YYYY-MM-DD)"""
        standardized = []
        for date in dates:
            try:
                # Add date parsing logic here
                standardized.append(date)
            except:
                continue
        return standardized

    def find_price(self, element) -> Optional[float]:
        """Extract price information"""
        price_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars'
        ]
        
        text = element.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    return float(re.sub(r'[^\d.]', '', matches[0]))
                except:
                    continue
        return None

    def find_age_range(self, element) -> Optional[str]:
        """Extract age range information"""
        age_patterns = [
            r'ages?\s*\d+\s*-\s*\d+',
            r'\d+\s*-\s*\d+\s*years?',
            r'grades?\s*\d+\s*-\s*\d+'
        ]
        
        text = element.get_text()
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def find_location(self, element) -> Optional[str]:
        """Extract location information"""
        location_patterns = [
            r'\b\d{1,5}\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Circle|Cir)\b',
            r'\b[A-Za-z\s]+(?:Center|Building|Campus|Location)\b'
        ]
        
        text = element.get_text()
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

