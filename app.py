import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import CampScraper
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

# Page configuration
st.set_page_config(
    page_title="Seattle Summer Camps Finder",
    page_icon="🏕️",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'camps_data' not in st.session_state:
        st.session_state.camps_data = []
    if 'last_search' not in st.session_state:
        st.session_state.last_search = None

def show_filters():
    """Show search filters in sidebar"""
    st.sidebar.header("Search Filters")
    
    # ZIP code and radius
    col1, col2 = st.sidebar.columns(2)
    with col1:
        zip_code = st.text_input("ZIP Code", "98101")
    with col2:
        radius = st.number_input("Search Radius (miles)", 
                               min_value=1, 
                               max_value=20, 
                               value=5)

    # Age range
    age = st.sidebar.number_input("Child's Age", 3, 18, 8)
    
    # Date range
    st.sidebar.subheader("Date Range")
    start_date = st.sidebar.date_input("Start Date", 
                                      datetime.strptime("2025-06-01", "%Y-%m-%d"))
    end_date = st.sidebar.date_input("End Date", 
                                    datetime.strptime("2025-08-31", "%Y-%m-%d"))
    
    # Price range
    max_price = st.sidebar.slider("Maximum Price ($)", 100, 1000, 500)
    
    return {
        "zip_code": zip_code,
        "radius": radius,
        "age": age,
        "start_date": start_date,
        "end_date": end_date,
        "max_price": max_price
    }

def search_camps(filters):
    """Search for camps using the scraper"""
    try:
        scraper = CampScraper()
        logging.info(f"Starting camp search with filters: {filters}")
        
        # Get camps using the new method
        camps = scraper.search_camps(filters)
        
        logging.info(f"Found {len(camps)} matching camps")
        return camps
        
    except Exception as e:
        logging.error(f"Error during search: {str(e)}")
        st.error(f"Error during search: {str(e)}")
        return []

def display_camps(camps):
    """Display camps in a nice format"""
    if not camps:
        st.warning("No camps found matching your criteria.")
        return
        
    st.success(f"Found {len(camps)} matching camps!")
    
    for camp in camps:
        with st.expander(f"{camp['name']} - {camp['provider']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Ages:** {camp['ages']}")
                st.write(f"**Cost:** ${camp['cost']}")
                st.write(f"**Location:** {camp['location']}")
            
            with col2:
                st.write("**Dates:**")
                for date in camp['dates']:
                    st.write(f"- {date}")
                
            if 'description' in camp:
                st.write("**Description:**:**")
                st.write(camp['description'])

def main():
    st.title("Seattle Summer Camps Finder 🏕️")
    
    initialize_session_state()
    
    # Show filters in sidebar
    filters = show_filters()
    
    # Search button
    if st.sidebar.button("Search Camps"):
        with st.spinner("Searching for camps..."):
            st.session_state.camps_data = search_camps(filters)
            st.session_state.search_performed = True
            st.session_state.last_search = datetime.now()
    
    # Display results
    if st.session_state.search_performed:
        display_camps(st.session_state.camps_data)
        
        # Download results
        if st.session_state.camps_data:
            df = pd.DataFrame(st.session_state.camps_data)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Results (CSV)",
                csv,
                "summer_camps.csv",
                "text/csv",
                key='download-csv'
            )
    
    # Show last search time
    if st.session_state.last_search:
        st.sidebar.caption(f"Last search: {st.session_state.last_search.strftime('%I:%M %p')}")

if __name__ == "__main__":
    main()
