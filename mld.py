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


# Functions for MLD Calculation
def calculate_mld(
    df, temp_col="Temperature [ITS90,°C]", depth_col="Depth [m]", threshold=0.5
):
    surface_temp = df[temp_col].iloc[0]
    mld = df[df[temp_col] <= surface_temp - threshold][depth_col].min()
    return mld if not np.isnan(mld) else df[depth_col].max()


# Centered Page layout
st.markdown(
    "<h1 style='text-align: center;'>Mixed Layer Depth Analysis from CTD Profiles 📏🌊</h1>",
    unsafe_allow_html=True,
)

# Access the shared data from session state
data = st.session_state.get("data")

if data is None:
    st.error(
        "Data not found in session state. Please load data in the main application."
    )
else:
    data["Lat (°S)"] = data["Lat (°S)"].apply(lambda x: -abs(x))

    # Sidebar filters
    st.sidebar.header("Filter data")
    grid_options = list(data["Grid"].unique())
    selected_grids = st.sidebar.multiselect(
        "Select Grid(s)", grid_options, default=[grid_options[1]]
    )

    # Season and Year filters
    selected_season = st.sidebar.multiselect(
        "Select Season(s)", data["season"].unique(), default=data["season"].unique()[0]
    )
    selected_year = st.sidebar.multiselect(
        "Select Year(s)",
        data.datetime.dt.year.dropna().unique(),
        default=data.datetime.dt.year.dropna().unique()[0],
    )

    # Filter data based on selection
    filtered_data = data[
        (data["Grid"].isin(selected_grids))
        & (data["season"].isin(selected_season))
        & (data["datetime"].dt.year.isin(selected_year))
    ]

    # Layout
    col1, col2 = st.columns([3, 7])

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
                marker=dict(size=6, symbol="circle", opacity=0.7, color="black")
            )
            st.plotly_chart(fig_map, use_container_width=True, config=config_figure)

        with col2:
            fig_mld = go.Figure()
            mld_values = []
            for season in selected_season:
                for station in filtered_data["Grid"].unique():
                    for year in selected_year:
                        station_data = filtered_data[
                            (filtered_data["Grid"] == station)
                            & (filtered_data["season"] == season)
                            & (filtered_data["datetime"].dt.year == year)
                        ]
                        if not station_data.empty:
                            station_data = station_data.sort_values("Depth [m]")
                            mld = calculate_mld(station_data)
                            mld_values.append((station, season, year, mld))

                            color = px.colors.qualitative.Plotly[
                                len(mld_values) % len(px.colors.qualitative.Plotly)
                            ]

                            fig_mld.add_trace(
                                go.Scatter(
                                    x=station_data["Temperature [ITS90,°C]"],
                                    y=station_data["Depth [m]"],
                                    mode="lines",
                                    name=f"{station} {season} {year}",
                                    line=dict(color=color),
                                )
                            )

                            fig_mld.add_trace(
                                go.Scatter(
                                    x=[
                                        station_data["Temperature [ITS90,°C]"].min(),
                                        station_data["Temperature [ITS90,°C]"].max(),
                                    ],
                                    y=[mld, mld],
                                    mode="lines",
                                    line=dict(color=color, dash="dash"),
                                    name="",  # Empty name to exclude from legend
                                    hovertemplate=f"MLD: {mld:.2f} m",
                                    showlegend=False,  # Do not show MLD in legend
                                )
                            )

            mld_text = "; ".join(
                [
                    f"{station} {season} {year}: {mld:.2f} m"
                    for station, season, year, mld in mld_values
                ]
            )
            fig_mld.update_layout(
                title=f"Mixed Layer Depth (0.5°C Threshold)",
                xaxis_title="Temperature [ITS90,°C]",
                yaxis_title="Depth [m]",
                yaxis=dict(autorange="reversed"),
                width=600,  # Set the width of the scatter plot
                height=520,
            )

            st.plotly_chart(fig_mld, config=config_figure)
    else:
        st.warning(
            "No data selected. Please select at least one grid to visualize the data."
        )
