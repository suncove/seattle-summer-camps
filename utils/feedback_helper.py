import streamlit as st
from database import Database
from datetime import datetime

def collect_feedback():
    """Collect and store user feedback"""
    st.header("📝 Feedback")
    
    with st.expander("Help us improve!"):
        # User rating
        rating = st.slider(
            "How would you rate your experience?",
            min_value=1,
            max_value=5,
            value=5
        )
        
        # Specific aspects rating
        col1, col2 = st.columns(2)
        with col1:
            ease_of_use = st.select_slider(
                "Ease of use:",
                options=["Very Difficult", "Difficult", "Neutral", "Easy", "Very Easy"],
                value="Easy"
            )
            
        with col2:
            search_results = st.select_slider(
                "Search results relevance:",
                options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
                value="Good"
            )
        
        # Comments
        comments = st.text_area(
            "Additional comments or suggestions:",
            height=100
        )
        
        # Would recommend
        would_recommend = st.radio(
            "Would you recommend this tool to other parents?",
            ["Yes", "Maybe", "No"]
        )
        
        # Submit button
        if st.button("Submit Feedback"):
            feedback = {
                "rating": rating,
                "ease_of_use": ease_of_use,
                "search_results": search_results,
                "comments": comments,
                "would_recommend": would_recommend,
                "timestamp": datetime.now().isoformat()
            }
            
            db = Database()
            if db.save_feedback(feedback):
                st.success("Thank you for your feedback!")
            else:
                st.error("Sorry, there was an error submitting your feedback.")

