import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio
import gsw

pio.kaleido.scope.default_format = "svg"
from functions import config_figure

from css import app_css  # Import CSS as a string

st.markdown(app_css, unsafe_allow_html=True)

# Page layout
st.markdown(
    "<h1 style='text-align: center;'>Water Masses Classification 🌊</h1>",
    unsafe_allow_html=True,
)

# Access the shared data from session state
data = st.session_state.get("data")

if data is None:
    st.error(
        "Data not found in session state. Please load data in the main application."
    )
else:
    # Cache the data transformation
    @st.cache_data
    def transform_data(df):
        df["Lat (°S)"] = df["Lat (°S)"].apply(lambda x: -abs(x))
        return df

    data = transform_data(data)

    # Initialize session state for sidebar filters if not already set
    if "grids_selected" not in st.session_state:
        default_station = (
            "NML10" if "NML10" in data["Grid"].unique() else data["Grid"].unique()[0]
        )
        st.session_state.grids_selected = [default_station]

    # Sidebar filters
    st.sidebar.header("Filter data")
    grid_options = ["All Stations"] + list(data["Grid"].unique())

    # Multiselect widget with session state
    grids_selected = st.sidebar.multiselect(
        "Select Grid(s)", grid_options, default=st.session_state.grids_selected
    )

    # Update session state
    st.session_state.grids_selected = grids_selected

    # Cache the "All Stations" data
    @st.cache_data
    def get_all_stations_data(df):
        return df

    # Filter data based on selection
    if "All Stations" in st.session_state.grids_selected:
        filtered_data = get_all_stations_data(data)
    else:
        filtered_data = data[data["Grid"].isin(st.session_state.grids_selected)]

    # Layout
    col1, col2 = st.columns(
        [3, 8]
    )  # Adjusted the column width to make the scatter plot wider

    if not filtered_data.empty:
        with col1:
            fig_map = px.scatter_mapbox(
                filtered_data,
                lat="Lat (°S)",
                lon="Lon (°E)",
                hover_name="Grid",
                zoom=4.5,
                height=600,
            )
            fig_map.update_layout(
                mapbox_style="open-street-map",
                mapbox_center={"lat": -33.0, "lon": 17.0},
            )
            fig_map.update_traces(
                marker=dict(size=4, symbol="circle", opacity=0.7, color="black")
            )
            st.plotly_chart(fig_map, use_container_width=True)

        with col2:
            # Water Mass Classification Plot

            fig_wm = go.Figure()

            if not filtered_data.empty:
                # Cache the isopycnals calculation
                @st.cache_data
                def calculate_isopycnals(filtered_data):
                    t_min = filtered_data["Temperature [ITS90,°C]"].min() - 1
                    t_max = filtered_data["Temperature [ITS90,°C]"].max() + 1
                    s_min = filtered_data["Salinity [psu]"].min() - 1
                    s_max = filtered_data["Salinity [psu]"].max() + 1

                    xdim = int(np.ceil((s_max - s_min) / 0.1))
                    ydim = int(np.ceil(t_max - t_min))
                    dens = np.zeros((ydim, xdim))

                    ti = np.linspace(t_min, t_max, ydim)
                    si = np.linspace(s_min, s_max, xdim)

                    for j in range(ydim):
                        for i in range(xdim):
                            dens[j, i] = gsw.rho(si[i], ti[j], 0)

                    dens = dens - 1000

                    return si, ti, dens

                si, ti, dens = calculate_isopycnals(filtered_data)

                # Add isopycnals to the plot
                fig_wm.add_trace(
                    go.Contour(
                        x=si,
                        y=ti,
                        z=dens,
                        contours_coloring="lines",
                        showscale=False,  # Hide the colorbar for isopycnals
                        contours=dict(
                            start=dens.min(),
                            end=dens.max(),
                            size=0.5,
                            showlabels=True,  # show labels on contours
                            labelfont=dict(  # label font properties
                                size=12,
                                color="black",
                            ),
                        ),
                        name="Isopycnals",
                    )
                )

                # Combine all stations into one trace to use a single colorbar
                fig_wm.add_trace(
                    go.Scatter(
                        x=filtered_data["Salinity [psu]"],
                        y=filtered_data["Temperature [ITS90,°C]"],
                        mode="markers",
                        marker=dict(
                            color=filtered_data["Pressure [db]"],
                            colorscale="spectral",  # Use the 'spectral' colormap
                            colorbar=dict(
                                title=dict(
                                    text="Pressure [db]",
                                    side="bottom",  # Place the title below the colorbar
                                ),
                                orientation="h",
                                x=0.5,
                                y=-0.4,  # Adjust the position to move the colorbar further from the map
                            ),
                            size=3,
                        ),
                        name="Stations",
                    )
                )

                # Water Mass Classification Annotations
                box_conditions = [
                    {
                        "name": "Antarctic Bottom Water",
                        "abbreviation": "ABW",
                        "temp_min": -2,
                        "temp_max": 2,
                        "sal_min": 34.6,
                        "sal_max": 34.8,
                        "dens_min": 27.9,
                        "dens_max": np.inf,
                        "color": "Black",
                    },
                    {
                        "name": "North Atlantic Deep Water",
                        "abbreviation": "NADW",
                        "temp_min": 2,
                        "temp_max": 4,
                        "sal_min": 34.9,
                        "sal_max": 35.0,
                        "dens_min": 27.8,
                        "dens_max": np.inf,
                        "color": "Black",
                    },
                    {
                        "name": "Low Salinity Antarctic Intermediate Water",
                        "abbreviation": "LSAIW",
                        "temp_min": 3,
                        "temp_max": 6,
                        "sal_min": 34.3,
                        "sal_max": 34.6,
                        "dens_min": 27.2,
                        "dens_max": 27.5,
                        "color": "Black",
                    },
                    {
                        "name": "High Salinity Antarctic Intermediate Water",
                        "abbreviation": "HSAIW",
                        "temp_min": 5,
                        "temp_max": 10,
                        "sal_min": 34.5,
                        "sal_max": 35.0,
                        "dens_min": 27.3,
                        "dens_max": 27.6,
                        "color": "Black",
                    },
                    {
                        "name": "Low Salinity Central Water",
                        "abbreviation": "LSCW",
                        "temp_min": 8,
                        "temp_max": 15,
                        "sal_min": 34.3,
                        "sal_max": 34.8,
                        "dens_min": 26.5,
                        "dens_max": 27.0,
                        "color": "Black",
                    },
                    {
                        "name": "High Salinity Central Water",
                        "abbreviation": "HSCW",
                        "temp_min": 8,
                        "temp_max": 15,
                        "sal_min": 34.8,
                        "sal_max": 35.5,
                        "dens_min": 26.8,
                        "dens_max": 27.4,
                        "color": "Black",
                    },
                    {
                        "name": "Modified Upwelled Water",
                        "abbreviation": "MUW",
                        "temp_min": 15,
                        "temp_max": 20,
                        "sal_min": 35.0,
                        "sal_max": 36.0,
                        "dens_min": 25.8,
                        "dens_max": 26.5,
                        "color": "Black",
                    },
                    {
                        "name": "Oceanic Surface Water",
                        "abbreviation": "OSW",
                        "temp_min": 20,
                        "temp_max": 30,
                        "sal_min": 34.5,
                        "sal_max": 36.5,
                        "dens_min": 24.0,
                        "dens_max": 25.5,
                        "color": "Black",
                    },
                ]

                for condition in box_conditions:
                    # Filter the data to match the water mass condition
                    condition_data = filtered_data[
                        (
                            filtered_data["Temperature [ITS90,°C]"]
                            >= condition["temp_min"]
                        )
                        & (
                            filtered_data["Temperature [ITS90,°C]"]
                            <= condition["temp_max"]
                        )
                        & (filtered_data["Salinity [psu]"] >= condition["sal_min"])
                        & (filtered_data["Salinity [psu]"] <= condition["sal_max"])
                        & (
                            filtered_data["Density Derived [sigma-theta, kg/m^3]"]
                            >= condition["dens_min"]
                        )
                        & (
                            filtered_data["Density Derived [sigma-theta, kg/m^3]"]
                            <= condition["dens_max"]
                        )
                    ]

                    if not condition_data.empty:
                        # Calculate the average position for annotation
                        avg_sal = condition_data["Salinity [psu]"].mean()
                        avg_temp = condition_data["Temperature [ITS90,°C]"].mean()

                        # Add a single annotation at the average position
                        fig_wm.add_annotation(
                            x=avg_sal,
                            y=avg_temp,
                            text=f"<b>{condition['abbreviation']}</b>",
                            showarrow=False,
                            font=dict(size=12, color=condition["color"]),
                            xanchor="center",
                            yanchor="bottom",
                        )

            fig_wm.update_layout(
                title="Water Mass Classification",
                xaxis_title=dict(text="Salinity [psu]", font=dict(color="black")),
                yaxis_title=dict(
                    text="Temperature [ITS90,°C]", font=dict(color="black")
                ),
                width=800,  # Set the width of the scatter plot
                height=600,
                showlegend=False,  # Ensure legend is displayed for stations
            )

            st.plotly_chart(fig_wm)

    else:
        st.warning(
            "No data selected. Please select at least one grid to visualize the data."
        )
