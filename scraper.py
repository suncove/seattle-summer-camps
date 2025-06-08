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
import time
import random

class CampScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.setup_logging()
        self.cache = {}
        
    def setup_logging(self):
        logging.basicConfig(
            filename='camp_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    # Main source categories
    CAMP_SOURCES = {
        'community_centers': [
            'https://www.seattle.gov/parks/find/centers',
            'https://www.bellevuewa.gov/city-government/departments/parks/community-centers',
        ],
        'museums': [
            'https://www.pacificsciencecenter.org/camps/',
            'https://www.mopop.org/programs-plus-education/',
            'https://www.seattleartmuseum.org/visit/calendar',
            'https://www.museumofflight.org/Education/Camps',
        ],
        'sports_facilities': [
            'https://www.seattleymca.org/programs/camp',
            'https://www.arena-sports.net/youth-programs',
        ],
        'arts_organizations': [
            'https://www.sct.org/classes-camps/',
            'https://www.seattleopera.org/classes/',
        ]
    }

    def get_camps(self) -> List[Dict]:
        """Get all camps from demo data"""
        # Using demo data for reliable results
        return [
            {
                "name": "STEM Discovery Camp",
                "provider": "Pacific Science Center",
                "ages": "8-12",
                "dates": ["2025-07-10", "2025-07-24"],
                "cost": 475.0,
                "location": "200 2nd Ave N, Seattle",
                "description": "Hands-on STEM exploration"
            },
            {
                "name": "Zoo Explorers",
                "provider": "Woodland Park Zoo",
                "ages": "7-11",
                "dates": ["2025-07-17"],
                "cost": 425.0,
                "location": "5500 Phinney Ave N, Seattle",
                "description": "Wildlife discovery"
            },
            # Add more demo camps here
            {
                "name": "Art Adventure Camp",
                "provider": "Seattle Art Museum",
                "ages": "6-12",
                "dates": ["2025-07-15", "2025-08-05"],
                "cost": 450.0,
                "location": "1300 1st Ave, Seattle",
                "description": "Creative art exploration"
            },
            {
                "name": "Drama Workshop",
                "provider": "Seattle Children's Theatre",
                "ages": "8-14",
                "dates": ["2025-07-08", "2025-07-22"],
                "cost": 495.0,
                "location": "201 Thomas St, Seattle",
                "description": "Theater arts"
            },
            {
                "name": "Science Explorers",
                "provider": "Museum of Flight",
                "ages": "9-13",
                "dates": ["2025-07-12", "2025-07-26"],
                "cost": 445.0,
                "location": "9404 E Marginal Way S, Seattle",
                "description": "Aviation and space"
            },
            {
                "name": "Music Camp",
                "provider": "MoPOP",
                "ages": "10-15",
                "dates": ["2025-07-09", "2025-07-23"],
                "cost": 485.0,
                "location": "325 5th Ave N, Seattle",
                "description": "Music and performance"
            },
            {
                "name": "Sports Multi-Camp",
                "provider": "Seattle YMCA",
                "ages": "7-12",
                "dates": ["2025-07-14", "2025-07-28"],
                "cost": 395.0,
                "location": "Multiple locations",
                "description": "Various sports activities"
            },
            {
                "name": "Nature Explorers",
                "provider": "Seattle Parks",
                "ages": "6-11",
                "dates": ["2025-07-16", "2025-07-30"],
                "cost": 375.0,
                "location": "Discovery Park",
                "description": "Outdoor adventure"
            },
            {
                "name": "Coding Camp",
                "provider": "Living Computers Museum",
                "ages": "11-15",
                "dates": ["2025-07-11", "2025-07-25"],
                "cost": 465.0,
                "location": "2245 1st Ave S, Seattle",
                "description": "Programming basics"
            },
            {
                "name": "Marine Biology Camp",
                "provider": "Seattle Aquarium",
                "ages": "8-13",
                "dates": ["2025-07-13", "2025-07-27"],
                "cost": 455.0,
                "location": "1483 Alaskan Way",
                "description": "Ocean exploration"
            }
        ]

    def search_camps(self, filters: Dict) -> List[Dict]:
        """Search camps based on filters"""
        all_camps = self.get_camps()
        filtered_camps = []

        for camp in all_camps:
            if self.matches_filters(camp, filters):
                filtered_camps.append(camp)

        return filtered_camps

    def matches_filters(self, camp: Dict, filters: Dict) -> bool:
        """Check if camp matches the given filters"""
        # Age filter
        camp_min_age, camp_max_age = map(int, camp['ages'].split('-'))
        if not (camp_min_age <= filters['age'] <= camp_max_age):
            return False

        # Price filter
        if camp['cost'] > filters.get('max_price', float('inf')):
            return False

        # Date filter
        if 'start_date' in filters and 'end_date' in filters:
            camp_dates = [datetime.strptime(date, "%Y-%m-%d") for date in camp['dates']]
            if not any(filters['start_date'] <= date.date() <= filters['end_date'] 
                      for date in camp_dates):
                return False

        return True

