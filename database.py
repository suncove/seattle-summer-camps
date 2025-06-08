import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json
import logging
from typing import Dict, List

class Database:
    def __init__(self):
        try:
            # Initialize Firebase
            cred = credentials.Certificate('firebase-credentials.json')
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            logging.error(f"Failed to initialize database: {str(e)}")
            self.db = None

    def save_camp_data(self, camps: List[Dict]):
        """Save scraped camp data to database"""
        if not self.db:
            return False
        
        try:
            batch = self.db.batch()
            camps_ref = self.db.collection('camps')
            
            for camp in camps:
                camp_doc = camps_ref.document()
                camp['last_updated'] = datetime.now()
                batch.set(camp_doc, camp)
            
            batch.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving camp data: {str(e)}")
            return False

    def save_feedback(self, feedback: Dict):
        """Save user feedback"""
        if not self.db:
            return False
        
        try:
            feedback['timestamp'] = datetime.now()
            self.db.collection('feedback').add(feedback)
            return True
        except Exception as e:
            logging.error(f"Error saving feedback: {str(e)}")
            return False

    def get_camp_stats(self):
        """Get statistics about camps"""
        if not self.db:
            return {}
        
        try:
            stats = {
                'total_camps': 0,
                'avg_price': 0,
                'popular_activities': {}
            }
            
            camps = self.db.collection('camps').stream()
            
            for camp in camps:
                camp_data = camp.to_dict()
                stats['total_camps'] += 1
                stats['avg_price'] += camp_data.get('price', 0)
                
                # Track activity popularity
                for activity in camp_data.get('activities', []):
                    stats['popular_activities'][activity] = \
                        stats['popular_activities'].get(activity, 0) + 1
            
            if stats['total_camps'] > 0:
                stats['avg_price'] /= stats['total_camps']
            
            return stats
        except Exception as e:
            logging.error(f"Error getting camp stats: {str(e)}")
            return {}

