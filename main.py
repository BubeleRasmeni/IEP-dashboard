import streamlit as st
import pandas as pd
#page setup
apptitle = "IEP Analysis 🌊"
st.set_page_config(page_title=apptitle, page_icon="🌊", layout='wide')
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
