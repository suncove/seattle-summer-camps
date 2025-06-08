import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import SeattleCampScraper as CampScraper
import logging
import json
import plotly.figure_factory as ff
import plotly.express as px
from datetime import timedelta
import uuid


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
        
        # Convert filter dates to datetime objects
        start_date = datetime.combine(filters['start_date'], datetime.min.time())
        end_date = datetime.combine(filters['end_date'], datetime.min.time())
        
        # Get camps from scraper
        camps = scraper.scrape_all_sources()
        
        # Filter camps based on criteria
        filtered_camps = []
        for camp in camps:
            try:
                # Check age range
                camp_min_age, camp_max_age = map(int, camp['ages'].split('-'))
                if camp_min_age <= filters['age'] <= camp_max_age:
                    # Check price
                    if camp['cost'] <= filters['max_price']:
                        # Check dates
                        camp_dates = [datetime.strptime(date, "%Y-%m-%d") for date in camp['dates']]
                        if any(start_date <= date <= end_date for date in camp_dates):
                            filtered_camps.append(camp)
                
            except Exception as e:
                logging.error(f"Error processing camp {camp['name']}: {str(e)}")
                continue
        
        logging.info(f"Found {len(filtered_camps)} matching camps")
        return filtered_camps
        
    except Exception as e:
        logging.error(f"Error searching camps: {str(e)}")
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
                
            st.write("**Description:**")
            st.write(camp['description'])
            
            if 'last_updated' in camp:
                st.caption(f"Last updated: {camp['last_updated']}")

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

def show_calendar_view(camps):
    """Create a calendar view of camps using plotly"""
    if not camps:
        return

    # Create timeline data
    timeline_data = []
    colors = px.colors.qualitative.Set3
    
    for i, camp in enumerate(camps):
        color = colors[i % len(colors)]
        for date in camp['dates']:
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=5)  # Assuming 5-day camps
            timeline_data.append(dict(
                Task=camp['name'],
                Start=start_date,
                Finish=end_date,
                Resource=camp['provider'],
                Description=f"${camp['cost']} • Ages {camp['ages']}",
                Color=color
            ))

    if timeline_data:
        fig = ff.create_gantt(timeline_data, 
                            colors=dict(zip([d['Task'] for d in timeline_data], 
                                          [d['Color'] for d in timeline_data])),
                            index_col='Resource',
                            show_colorbar=True,
                            group_tasks=True,
                            showgrid_x=True,
                            showgrid_y=True)
        
        fig.update_layout(
            title="Summer Camps Timeline",
            height=400,
            xaxis_title="Date",
            yaxis_title="Camp Provider"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'camps_data' not in st.session_state:
        st.session_state.camps_data = []
    if 'favorite_camps' not in st.session_state:
        st.session_state.favorite_camps = []

def toggle_favorite(camp):
    """Add or remove camp from favorites"""
    camp_id = f"{camp['name']}_{camp['provider']}"
    if camp_id in st.session_state.favorite_camps:
        st.session_state.favorite_camps.remove(camp_id)
        return False
    else:
        st.session_state.favorite_camps.append(camp_id)
        return True

def display_camps(camps):
    """Display camps in a nice format with calendar view option"""
    if not camps:
        st.warning("No camps found matching your criteria.")
        return
        
    st.success(f"Found {len(camps)} matching camps!")
    
    # View options
    view_type = st.radio("Select View", ["List", "Calendar"], horizontal=True)
    
    if view_type == "Calendar":
        show_calendar_view(camps)
    
    for camp in camps:
        with st.expander(f"{camp['name']} - {camp['provider']}"):
            col1, col2, col3 = st.columns([2,2,1])
            
            with col1:
                st.write(f"**Ages:** {camp['ages']}")
                st.write(f"**Cost:** ${camp['cost']}")
                st.write(f"**Location:** {camp['location']}")
            
            with col2:
                st.write("**Dates:**")
                for date in camp['dates']:
                    st.write(f"- {date}")
                
            with col3:
                camp_id = f"{camp['name']}_{camp['provider']}"
                is_favorite = camp_id in st.session_state.favorite_camps
                if st.button(
                    "★ Favorite" if is_favorite else "☆ Add to Favorites",
                    key=f"fav_{camp_id}"
                ):
                    is_favorite = toggle_favorite(camp)
            
            st.write("**Description:**")
            st.write(camp['description'])

    # Show favorites
    if st.session_state.favorite_camps:
        st.sidebar.markdown("---")
        st.sidebar.header("My Favorite Camps")
        for camp_id in st.session_state.favorite_camps:
            st.sidebar.write(f"★ {camp_id.split('_')[0]}")

