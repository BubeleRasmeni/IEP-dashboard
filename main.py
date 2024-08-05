import streamlit as st
################################################################
# Page Setup
apptitle = "IEP Analysis"
st.set_page_config(page_title=apptitle, page_icon="🌊", layout='wide')
# Add an image to the sidebar
#st.logo(r"C:\Users\brasmeni\Desktop\WORK\MIMS\IEP dashboard\images\science-vessel.jpg")
# Define the available pages
pages = {
    "Information":[
        st.Page("about.py", title="IEP Project"),],
    "Data Exploration":[
        st.Page("data_explorer.py", title="Data Visualisation")
    ],
     "Water Masses and MLD":[
        st.Page("advanced_analysis.py", title="Water Mass Classification and MLD")
    ]
}

# Create the navigation
pg = st.navigation(pages)

# Run the selected page
pg.run()
