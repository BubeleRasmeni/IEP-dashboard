import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio
import gsw
pio.kaleido.scope.default_format = "svg"
from functions import config_figure

st.set_page_config(layout="wide")

# Functions for MLD and Water Mass Classification
def calculate_mld(df, temp_col='Temperature [ITS90,°C]', depth_col='Depth [m]', threshold=0.5):
    surface_temp = df[temp_col].iloc[0]
    mld = df[df[temp_col] <= surface_temp - threshold][depth_col].min()
    return mld if not np.isnan(mld) else df[depth_col].max()

# Page layout
st.title("Welcome to IEP Interactive Data Visualisation 🚢 🐋")

@st.cache_data
def load_data():
    df = pd.read_excel('data/IEP_2017_2018.xlsx')
    return df

data = load_data()
data['Lat (°S)'] = data['Lat (°S)'].apply(lambda x: -abs(x))

# Sidebar filters
st.sidebar.header("Filter data")
selected_grids = st.sidebar.multiselect('Select Grid(s)', data['Grid'].unique(), default=data['Grid'].unique()[0])

start_date = st.sidebar.date_input(
    'Start Date',
    min_value=data['datetime'].min().date(),
    max_value=data['datetime'].max().date(),
    value=data['datetime'].min().date()
)
end_date = st.sidebar.date_input(
    'End Date',
    min_value=data['datetime'].min().date(),
    max_value=data['datetime'].max().date(),
    value=data['datetime'].max().date()
)

if start_date > end_date:
    st.sidebar.error('Error: End date must fall after start date.')

selected_time = (start_date, end_date)

if selected_grids:
    filtered_data = data[(data['Grid'].isin(selected_grids)) & 
                         (data['datetime'].dt.date.between(selected_time[0], selected_time[1]))]
else:
    filtered_data = data[(data['Grid'].isin(selected_grids)) & 
                         (data['datetime'].dt.date.between(selected_time[0], selected_time[1]))]

# Layout
col1, col2 = st.columns([7, 3])

with col1:
    fig_map = px.scatter_mapbox(filtered_data, lat='Lat (°S)', lon='Lon (°E)', hover_name='Grid', zoom=4.5, height=600)
    fig_map.update_layout(mapbox_style="open-street-map", mapbox_center={"lat": -33.0, "lon": 17.0})
    fig_map.update_traces(marker=dict(size=6, symbol='circle', opacity=0.7, color='black'))
    st.plotly_chart(fig_map, use_container_width=True, config=config_figure)

with col2:
    st.header("Analysis Options")
    analysis_option = st.radio('Choose an Analysis 👇', ['Mixed Layer Depth (MLD)', 'Water Mass Classification'])
    st.markdown("Scroll down to see " + analysis_option)

if analysis_option == 'Mixed Layer Depth (MLD)':
    st.header('Mixed Layer Depth (MLD) Analysis')
    col1, col2 = st.columns(2)
    with col1:
        selected_season = st.multiselect('Select Season(s)', filtered_data['season'].unique(), default=filtered_data['season'].unique()[0])
    with col2:
        selected_year = st.multiselect('Select Year(s)', filtered_data.datetime.dt.year.dropna().unique(), default=[filtered_data.datetime.dt.year.dropna().unique()[0]])

    fig_mld = go.Figure()
    mld_values = []
    for season in selected_season:
        for station in filtered_data['Grid'].unique():
            for year in selected_year:
                station_data = filtered_data[(filtered_data['Grid'] == station) &
                                             (filtered_data['season'] == season) & (filtered_data['datetime'].dt.year == year)]
                if not station_data.empty:
                    station_data = station_data.sort_values('Depth [m]')
                    mld = calculate_mld(station_data)
                    mld_values.append((station, season, year, mld))

                    color = px.colors.qualitative.Plotly[len(mld_values) % len(px.colors.qualitative.Plotly)]

                    fig_mld.add_trace(go.Scatter(
                        x=station_data['Temperature [ITS90,°C]'],
                        y=station_data['Depth [m]'],
                        mode='lines',
                        name=f'{station} {season} {year}',
                        line=dict(color=color)
                    ))

                    fig_mld.add_trace(go.Scatter(
                        x=[station_data['Temperature [ITS90,°C]'].min(), station_data['Temperature [ITS90,°C]'].max()],
                        y=[mld, mld],
                        mode="lines",
                        line=dict(color=color, dash='dash'),
                        name=f'{station} {season} {year} MLD',
                        hovertemplate=f'MLD: {mld:.2f} m'
                    ))

    mld_text = "; ".join([f'{station} {season} {year}: {mld:.2f} m' for station, season, year, mld in mld_values])
    fig_mld.update_layout(
        title=f'Mixed Layer Depth ({mld_text})',
        xaxis_title='Temperature [ITS90,°C]',
        yaxis_title='Depth [m]',
        yaxis=dict(autorange='reversed')
    )

    st.plotly_chart(fig_mld, config=config_figure)

elif analysis_option == 'Water Mass Classification':
    st.header('Water Mass Classification')
    col1, col2 = st.columns(2)
    with col1:
        selected_season = st.multiselect('Select Season(s)', filtered_data['season'].unique(), default=filtered_data['season'].unique()[0])
    with col2:
        selected_year = st.multiselect('Select Year(s)', filtered_data.datetime.dt.year.dropna().unique(), default=[filtered_data.datetime.dt.year.dropna().unique()[0]])

    # Filter data for selected stations, seasons, and years
    selected_data = filtered_data[(filtered_data['season'].isin(selected_season)) & 
                                  (filtered_data['datetime'].dt.year.isin(selected_year))]

    fig_wm = go.Figure()

    if not selected_data.empty:
        # Define the min / max values for plotting isopycnals based on selected data
        t_min = selected_data['Temperature [ITS90,°C]'].min() - 1
        t_max = selected_data['Temperature [ITS90,°C]'].max() + 1
        s_min = selected_data['Salinity [psu]'].min() - 1
        s_max = selected_data['Salinity [psu]'].max() + 1

        # Calculate how many gridcells we need in the x and y dimensions
        xdim = int(np.ceil((s_max - s_min) / 0.1))
        ydim = int(np.ceil(t_max - t_min))
        dens = np.zeros((ydim, xdim))

        # Create temp and salt vectors of appropriate dimensions
        ti = np.linspace(t_min, t_max, ydim)
        si = np.linspace(s_min, s_max, xdim)

        # Loop to fill in grid with densities
        for j in range(ydim):
            for i in range(xdim):
                dens[j, i] = gsw.rho(si[i], ti[j], 0)

        # Subtract 1000 to convert to sigma-t
        dens = dens - 1000

        # Add isopycnals to the plot
        fig_wm.add_trace(go.Contour(
            x=si,
            y=ti,
            z=dens,
            contours_coloring='lines',
            showscale=False,  # Hide the colorbar
            contours=dict(
                start=dens.min(),
                end=dens.max(),
                size=0.5,
                showlabels=True, # show labels on contours
                labelfont=dict( # label font properties
                    size=12,
                    color='black',
                ),
            ),
            name='Isopycnals'
        ))

    box_conditions = [
        {
            "name": "SACW",
            "temp_min": 8,
            "temp_max": 16,
            "sal_min": 34.72,
            "sal_max": 35.64,
            "dens_min": 26.5,
            "dens_max": 27.3,
            "color": "Red"
        },
        {
            "name": "AAIW",
            "temp_min": 2,
            "temp_max": 7,
            "sal_min": 34.2,
            "sal_max": 34.5,
            "dens_min": 27.1,
            "dens_max": 27.6,
            "color": "Green"
        },
                {
            "name": "ESACW",
            "temp_min": 5.95,
            "temp_max": 14.45,
            "sal_min": 34.41,
            "sal_max": 35.30,
            "dens_min": 27.1,
            "dens_max": 27.6,
            "color": "black"
        },
        {
            "name": "SAMW",
            "temp_min": 8,
            "temp_max": 12,
            "sal_min": 34.2,
            "sal_max": 34.6,
            "dens_min": 26.8,
            "dens_max": 27.2,
            "color": "Blue"
        },
        {
            "name": "NADW",
            "temp_min": 2,
            "temp_max": 4,
            "sal_min": 34.9,
            "sal_max": 35.0,
            "dens_min": 27.8,
            "dens_max": np.inf,  # Use np.inf to represent values greater than 27.8
            "color": "RoyalBlue"
        }
    ]

    for season in selected_season:
        for station in selected_data['Grid'].unique():
            for year in selected_year:
                station_data = selected_data[(selected_data['Grid'] == station) &
                                             (selected_data['season'] == season) & 
                                             (selected_data['datetime'].dt.year == year)]
                if not station_data.empty:
                    fig_wm.add_trace(go.Scatter(
                        x=station_data['Salinity [psu]'],
                        y=station_data['Temperature [ITS90,°C]'],
                        mode='markers',
                        name=f'{station} {season} {year}'
                    ))

                    for condition in box_conditions:
                        condition_data = station_data[
                            (station_data['Temperature [ITS90,°C]'].between(condition["temp_min"], condition["temp_max"])) &
                            (station_data['Salinity [psu]'].between(condition["sal_min"], condition["sal_max"])) &
                            (station_data['Density Derived [sigma-theta, kg/m^3]'].between(condition["dens_min"], condition["dens_max"]))
                        ]

                        if not condition_data.empty:
                            fig_wm.add_shape(
                                type="rect",
                                x0=condition["sal_min"],
                                x1=condition["sal_max"],
                                y0=condition["temp_min"],
                                y1=condition["temp_max"],
                                line=dict(color=condition["color"]),
                                name=condition["name"]
                            )
                            fig_wm.add_annotation(
                                x=(condition["sal_min"] + condition["sal_max"]) / 2,
                                y=condition["temp_max"],
                                text=condition["name"],
                                showarrow=False,
                                yshift=10,
                                font=dict(
                                    color=condition["color"]
                                )
                            )

    fig_wm.update_layout(
        title='Water Mass Classification',
        xaxis_title='Salinity [psu]',
        yaxis_title='Temperature [ITS90,°C]'
    )

    st.plotly_chart(fig_wm, config=config_figure)
