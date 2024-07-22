import streamlit as st
import pandas as pd
from functions import config_figure
import plotly.express as px
###########
@st.cache_data
def load_data():
    # Load data from the Excel file
    df = pd.read_excel('data/IEP_2017_2018_Stations.xlsx')
    return df

stations = load_data()

st.markdown("""
<style>
.small-text {
    font-size:16px !important;
    text-align: justify;  /* Justify the small text */
}
.center-text {
    text-align: center;  /* Center-align the main title */
}
</style>
""", unsafe_allow_html=True)

# Create the layout with three columns
col1, col2, col3 = st.columns([1, 18, 1])  # 5%, 90%, 5%

with col1:
    st.empty()  # Empty column to take 5% space on the left

with col2:
    title = """
    <h2 class='center-text' style='font-size:35px;'>Integrated Ecosystem Programme: Southern Benguela (IEP: SB) &#x1F6A2; &#x1F40B;🐬 🔬</h2>
    """
    st.markdown(title, unsafe_allow_html=True)

    st.markdown("""
    <p class="small-text" >
    Welcome to the Integrated Ecosystem Programme: Southern Benguela (IEP:SB) Analysis Dashboard.
    The IEP:SB is a multi-disciplinary project designed to undertake relevant science in the 
    Southern Benguela region. The primary objective of the IEP:SB is to develop ecosystem indicators that can be used to effectively monitor and 
    understand the Southern Benguela. These indicators cover a wide range of ecosystem components, 
    including physical, chemical, planktonic, microbial, seabird, and benthic elements. 
    The data and insights gained from this program are crucial for ecosystem-based management and conservation efforts.
    It serves as a platform for collaboration and learning, bringing together scientists and researchers from various disciplines to study the complex interactions within this marine ecosystem.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p class="small-text">
    This dashboard allows you to explore and visualise the CTD data collected during IEP voyages. 
    You can filter the data by grid, date range, and season, and visualize it through various types of plots, including profile plots, TS diagrams, and correlation heatmaps. 
    Each plot comes with a download option, enabling you to save the figures in different formats for further use offline.
    The data used here is published online in South Africa's Marine Information Management System (MIMS). The link to MIMS is available on the resource section.
    </p>
    """, unsafe_allow_html=True)

with col3:
    st.empty()  # Empty column to take 5% space on the right

# Create the layout with three columns for the map
col0, col1, col2 = st.columns([1, 18, 1])  # 5%, 90%, 5%

with col1:
    # Scatter map of sampling stations
    fig_stations = px.scatter_mapbox(stations, lat='Lat (°S)', lon='Lon (°E)', hover_name='Grid', zoom=4.5, height=600)
    fig_stations.update_layout(mapbox_style="open-street-map", mapbox_center={"lat": -33.0, "lon": 20.0})
    # Update marker style with different colors
    fig_stations.update_traces(
        marker=dict(
            size=6,
            symbol='circle',
            opacity=0.7,
            color='black'  # Example RGB color
        )
    )
    
    # Update legend layout
    fig_stations.update_layout(
        title="Sampling Stations for IEP",
        legend=dict(
            title="Legend",
            x=0.8,
            y=1,
            bgcolor='rgba(255, 255, 255, 0.7)'
        )
    )

    st.plotly_chart(fig_stations, use_container_width=True, config=config_figure)

# Sidebar content
st.sidebar.header("Resources")
st.sidebar.markdown(
    """
- [Marine Information Management System](https://data.ocean.gov.za/)
- [DFFE Oceans and Coasts](https://www.dffe.gov.za/OceansandCoastsManagement)
- [Python](https://www.python.org/) (Getting Started with Python)
- [Streamlit](https://docs.streamlit.io/)
"""
)
