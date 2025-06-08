import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from typing import Dict, List

# Updated camp data with standardized date format
SEATTLE_CAMPS = {
    "Pacific Science Center": [
        {
            "name": "STEM Discovery Camp",
            "age_range": "8-12",
            "dates": ["2025-07-10", "2025-07-24"],
            "cost": 475,
            "location": "200 2nd Ave N, Seattle",
            "registration_link": "pacificsciencecenter.org/camps",
            "rating": 4.8,
            "reviews": [
                {"user": "Parent123", "rating": 5, "comment": "Excellent STEM activities!"},
                {"user": "SeattleMom", "rating": 4.5, "comment": "Great instructors"}
            ],
            "capacity": 20,
            "current_bookings": 12,
            "activities": ["Robotics", "Chemistry", "Physics", "Coding"],
            "description": "Hands-on STEM exploration for curious minds"
        }
    ],
    "Woodland Park Zoo": [
        {
            "name": "Zoo Explorers",
            "age_range": "9-11",
            "dates": ["2025-07-17"],
            "cost": 425,
            "location": "5500 Phinney Ave N, Seattle",
            "registration_link": "zoo.org/camps",
            "rating": 4.9,
            "reviews": [
                {"user": "ZooLover", "rating": 5, "comment": "Amazing animal encounters!"},
                {"user": "SeattleDad", "rating": 4.8, "comment": "Educational and fun"}
            ],
            "capacity": 15,
            "current_bookings": 8,
            "activities": ["Animal Care", "Conservation", "Wildlife Study"],
            "description": "Discover wildlife and conservation"
        }
    ],
    "Moss Bay": [
        {
            "name": "Youth Kayaking Adventure",
            "age_range": "10-13",
            "dates": ["2025-07-08", "2025-07-22"],
            "cost": 495,
            "location": "1001 Fairview Ave N, Seattle",
            "registration_link": "mossbay.net/youth-camps",
            "rating": 4.7,
            "reviews": [
                {"user": "WaterSports", "rating": 4.7, "comment": "Great water safety instruction"},
                {"user": "KayakMom", "rating": 4.7, "comment": "Fun on the water"}
            ],
            "capacity": 12,
            "current_bookings": 6,
            "activities": ["Kayaking", "Water Safety", "Navigation"],
            "description": "Adventure on Seattle's waters"
        }
    ],
    "Seattle Children's Theatre": [
        {
            "name": "Drama Workshop",
            "age_range": "8-14",
            "dates": ["2025-07-15", "2025-08-05"],
            "cost": 450,
            "location": "201 Thomas St, Seattle",
            "registration_link": "sct.org/camps",
            "rating": 4.9,
            "reviews": [
                {"user": "TheatreMom", "rating": 5, "comment": "Wonderful creative experience"},
                {"user": "ArtsDad", "rating": 4.8, "comment": "Built confidence"}
            ],
            "capacity": 18,
            "current_bookings": 10,
            "activities": ["Acting", "Improvisation", "Stage Design"],
            "description": "Develop theater skills and confidence"
        }
    ],
    "Seattle YMCA": [
        {
            "name": "Multi-Sport Camp",
            "age_range": "7-12",
            "dates": ["2025-07-01", "2025-07-29"],
            "cost": 395,
            "location": "1426 NW 42nd St, Seattle",
            "registration_link": "seattleymca.org/camps",
            "rating": 4.6,
            "reviews": [
                {"user": "SportsFan", "rating": 4.6, "comment": "Great variety of activities"},
                {"user": "ActiveKidMom", "rating": 4.6, "comment": "Well-organized sports"}
            ],
            "capacity": 25,
            "current_bookings": 15,
            "activities": ["Basketball", "Soccer", "Swimming", "Tennis"],
            "description": "Active fun with multiple sports"
        }
    ]
}

class CampBookingSystem:
    def __init__(self):
        self.bookings = {}
        
    def book_camp(self, camp_name: str, date: str, user_info: Dict) -> str:
        booking_id = str(uuid.uuid4())
        self.bookings[booking_id] = {
            "camp_name": camp_name,
            "date": date,
            "user_info": user_info,
            "status": "confirmed"
        }
        return booking_id
    
    def check_conflicts(self, user_email: str, new_date: str) -> bool:
        for booking in self.bookings.values():
            if (booking["user_info"]["email"] == user_email and 
                booking["date"] == new_date):
                return True
        return False

def create_streamlit_app():
    st.title("Seattle Summer Camp Finder")
    
    # Sidebar filters
    st.sidebar.header("Search Filters")
    
    # Age filter
    age = st.sidebar.slider("Child's Age", 5, 15, 10)
    
    # Date filter
    start_date = st.sidebar.date_input("Start Date", 
                                      datetime.strptime("2025-07-01", "%Y-%m-%d"))
    
    # Cost filter
    max_cost = st.sidebar.slider("Maximum Cost ($)", 300, 1000, 500)
    
    # Activity preference
    all_activities = set()
    for provider in SEATTLE_CAMPS.values():
        for camp in provider:
            all_activities.update(camp["activities"])
    selected_activities = st.sidebar.multiselect("Preferred Activities", 
                                               list(sorted(all_activities)))
    
    # Rating filter
    min_rating = st.sidebar.slider("Minimum Rating", 3.0, 5.0, 4.0)
    
    # Initialize booking system
    booking_system = CampBookingSystem()
    
    # Process and display results
    matching_camps = []
    
    for provider, camps in SEATTLE_CAMPS.items():
        for camp in camps:
            # Apply filters
            age_min, age_max = map(int, camp["age_range"].split("-"))
            if (age >= age_min and age <= age_max and
                camp["cost"] <= max_cost and
                camp["rating"] >= min_rating and
                (not selected_activities or 
                 any(activity in camp["activities"] 
                     for activity in selected_activities))):
                
                # Check dates
                camp_dates = [datetime.strptime(date, "%Y-%m-%d") 
                            for date in camp["dates"]]
                if any(date.month == start_date.month for date in camp_dates):
                    # Format dates for display
                    formatted_dates = [date.strftime("%B %d, %Y") 
                                    for date in camp_dates]
                    camp_display = {**camp, 
                                  "provider": provider,
                                  "display_dates": formatted_dates}
                    matching_camps.append(camp_display)
    
    # Display results
    if matching_camps:
        st.write(f"Found {len(matching_camps)} matching camps:")
        
        for camp in matching_camps:
            with st.expander(f"{camp['name']} - {camp['provider']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Ages:** {camp['age_range']}")
                    st.write(f"**Cost:** ${camp['cost']}")
                    st.write(f"**Rating:** {camp['rating']}/5.0")
                    st.write(f"**Location:** {camp['location']}")
                
                with col2:
                    st.write(f"**Activities:** {', '.join(camp['activities'])}")
                    st.write(f"**Available Spots:** {camp['capacity'] - camp['current_bookings']}")
                    st.write(f"**Dates:** {', '.join(camp['display_dates'])}")
                
                # Reviews section
                st.write("**Reviews:**")
                for review in camp['reviews']:
                    st.write(f"_{review['comment']}_ - {review['user']}")
                
                # Booking section
                if st.button(f"Book {camp['name']}", key=camp['name']):
                    with st.form(f"booking_form_{camp['name']}"):
                        email = st.text_input("Email")
                        phone = st.text_input("Phone")
                        selected_date = st.selectbox("Select Session", camp['display_dates'])
                        
                        if st.form_submit_button("Confirm Booking"):
                            if booking_system.check_conflicts(email, selected_date):
                                st.error("You already have a camp booked for these dates!")
                            else:
                                booking_id = booking_system.book_camp(
                                    camp['name'],
                                    selected_date,
                                    {"email": email, "phone": phone}
                                )
                                st.success(f"Booking confirmed! ID: {booking_id}")
    
    else:
        st.write("No camps found matching your criteria.")
    
    # Export results
    if matching_camps:
        df = pd.DataFrame(matching_camps)
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Results as CSV",
            csv,
            "seattle_summer_camps.csv",
            "text/csv",
            key='download-csv'
        )

if __name__ == "__main__":
    create_streamlit_app()
