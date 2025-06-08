from typing import List, Dict
from datetime import datetime

def process_camp_data(camps: List[Dict], filters: Dict) -> List[Dict]:
    """Process and filter camp data based on user filters"""
    filtered_camps = []
    
    for camp in camps:
        if matches_filters(camp, filters):
            filtered_camps.append(camp)
    
    return sort_camps(filtered_camps)

def matches_filters(camp: Dict, filters: Dict) -> bool:
    """Check if camp matches all specified filters"""
    # Check age requirements
    camp_min_age, camp_max_age = map(int, camp['ages'].split('-'))
    if not any(
        camp_min_age <= age <= camp_max_age 
        for age in filters['children_ages']
    ):
        return False
    
    # Check price
    if camp['price'] > filters['max_price']:
        return False
    
    # Check dates
    camp_dates = [
        datetime.strptime(date, "%Y-%m-%d") 
        for date in camp['dates']
    ]
    if not any(
        filters['start_date'] <= date <= filters['end_date']
        for date in camp_dates
    ):
        return False
    
    # Check activities
    if filters['activities']:
        if not any(
            activity in camp['activities'] 
            for activity in filters['activities']
        ):
            return False
    
    return True

def sort_camps(camps: List[Dict]) -> List[Dict]:
    """Sort camps by distance and then price"""
    return sorted(
        camps,
        key=lambda x: (x.get('distance', 0), x.get('price', 0))
    )

