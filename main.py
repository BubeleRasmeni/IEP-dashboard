import streamlit as st
import pandas as pd

# Page setup
apptitle = "IEP Analysis 🌊"
st.set_page_config(page_title=apptitle, page_icon="🌊", layout='wide')

# Custom CSS for styling headers and footer
st.markdown(
    """
    <style>
    /* Page title styling */
    .css-18ni7ap h1 {
        font-size: 3rem; /* Page title font size */
        color: #1a73e8; /* Blue color */
        font-weight: bold;
        text-align: center;
    }

    /* Header styling (h2, h3) */
    h2 {
        color: #0d47a1; /* Darker blue for headers */
        font-weight: bold;
        margin-top: 1.5rem;
    }
    h3 {
        color: #1565c0; /* Slightly lighter blue for sub-headers */
        margin-top: 1rem;
    }

    /* Footer styling */
    footer {
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background-color: #f0f4fc; /* Light blue background */
        border-top: 1px solid #d1d9e6; /* Light grey border */
        color: #4a4a4a; /* Neutral grey text color */
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load data once and store it in session state
if 'data' not in st.session_state:
    @st.cache_data
    def load_data():
        df = pd.read_excel('data/IEP_2017_2018.xlsx')
        return df
    
    st.session_state.data = load_data()

# Define the available pages
pages = {
    "Information": [
        st.Page("about.py", title="📄 IEP Project"),
    ],
    "Data Exploration": [
        st.Page("data_explorer.py", title="📊 Data Visualization")
    ],
    "Water Masses": [
        st.Page("watermasses.py", title="🌊 Water Mass Classification")
    ],
    "Mixed Layer Depth": [
        st.Page("mld.py", title="📏 Mixed Layer Depth")
    ]
}

# Create the navigation
pg = st.navigation(pages)

# Run the selected page
pg.run()

# Add a footer
st.markdown(
    """
    <footer>
        Developed for IEP Analysis © 2024 | Powered by Streamlit 🌊
    </footer>
    """,
    unsafe_allow_html=True,
)
