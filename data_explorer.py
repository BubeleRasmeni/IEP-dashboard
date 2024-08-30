import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.io as pio

pio.kaleido.scope.default_format = "svg"
from functions import generate_correlation_heatmap, config_figure
import statsmodels.api as sm

# Page layout
st.markdown(
    "<h1 style='text-align: left;'>Explore the data 📊 📉</h1>",
    unsafe_allow_html=True,
)

# Access the shared data from session state
data = st.session_state.get("data")

if data is None:
    st.error(
        "Data not found in session state. Please load data in the main application."
    )
else:
    # Ensure all latitude values are negative
    data["Lat (°S)"] = data["Lat (°S)"].apply(lambda x: -abs(x))

    # Initialize session state for sidebar filters if not already set
    if "selected_grids" not in st.session_state:
        st.session_state.selected_grids = [data["Grid"].unique()[0]]
    if "selected_season" not in st.session_state:
        st.session_state.selected_season = [data["season"].unique()[0]]
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = [data.datetime.dt.year.dropna().unique()[0]]

    # Sidebar filters
    st.sidebar.header("Filter data")
    selected_grids = st.sidebar.multiselect(
        "Select Grid(s)", data["Grid"].unique(), default=st.session_state.selected_grids
    )
    selected_season = st.sidebar.multiselect(
        "Select Season(s)",
        data["season"].unique(),
        default=st.session_state.selected_season,
    )
    selected_year = st.sidebar.multiselect(
        "Select Year(s)",
        data.datetime.dt.year.dropna().unique(),
        default=st.session_state.selected_year,
    )

    # Update session state
    st.session_state.selected_grids = selected_grids
    st.session_state.selected_season = selected_season
    st.session_state.selected_year = selected_year

    if selected_grids:
        filtered_data = data[
            (data["Grid"].isin(selected_grids))
            & (data["season"].isin(selected_season))
            & (data["datetime"].dt.year.isin(selected_year))
        ]
    else:
        filtered_data = pd.DataFrame()  # Empty DataFrame if no grids are selected

    # Layout
    col1, col2 = st.columns([7, 3])

    if not filtered_data.empty:
        with col1:
            # Scatter map of sampling stations
            fig_map = px.scatter_mapbox(
                filtered_data,
                lat="Lat (°S)",
                lon="Lon (°E)",
                hover_name="Grid",
                zoom=4.5,
                height=600,
                width=700,
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
            st.header(" ")
            analysis_option = st.radio(
                "Choose a Figure 👇",
                [
                    "CTD Profiles",
                    "Regression Diagram",
                    "Box Plot",
                    "Correlation Heatmap",
                ],
            )
            st.markdown("Scroll down to see " + analysis_option)

        if analysis_option == "CTD Profiles":
            st.header("Profile Plot", anchor=None)
            col1, col2, col3 = st.columns(3)
            with col1:
                var_temp = st.selectbox(
                    "Select Temperature Variable",
                    ["Temperature [ITS90,°C]"],
                    key="temp",
                )
            with col2:
                var_sal = st.selectbox(
                    "Select Salinity Variable",
                    ["Salinity [psu]"],
                    key="sal",
                )
            with col3:
                var_oxy = st.selectbox(
                    "Select Variable",
                    ["Oxygen [ml/l]", "Flourescence [mg/m^3]"],
                    key="oxy",
                )

            fig = make_subplots(
                rows=1, cols=3, shared_yaxes=False, horizontal_spacing=0.15
            )

            for season in selected_season:
                for station in filtered_data["Grid"].unique():
                    for year in selected_year:
                        station_data = filtered_data[
                            (filtered_data["Grid"] == station)
                            & (filtered_data["season"] == season)
                            & (filtered_data["datetime"].dt.year == year)
                        ]
                        if not station_data.empty:
                            fig.add_trace(
                                go.Scatter(
                                    x=station_data[var_temp],
                                    y=station_data["Depth [m]"],
                                    mode="lines",
                                    name=f"{station} {season} Temp {year}",
                                ),
                                row=1,
                                col=1,
                            )
                            fig.add_trace(
                                go.Scatter(
                                    x=station_data[var_sal],
                                    y=station_data["Depth [m]"],
                                    mode="lines",
                                    name=f"{station} {season} Sal {year}",
                                ),
                                row=1,
                                col=2,
                            )
                            fig.add_trace(
                                go.Scatter(
                                    x=station_data[var_oxy],
                                    y=station_data["Depth [m]"],
                                    mode="lines",
                                    name=f"{station} {season} Oxy {year}",
                                ),
                                row=1,
                                col=3,
                            )

            fig.update_xaxes(title_text=var_temp, row=1, col=1)
            fig.update_xaxes(title_text=var_sal, row=1, col=2)
            fig.update_xaxes(title_text=var_oxy, row=1, col=3)
            fig.update_yaxes(title_text="Depth [m]", autorange="reversed")
            st.plotly_chart(fig, use_container_width=True, config=config_figure)

        elif analysis_option == "Regression Diagram":
            st.header("Regression Diagram")
            col1, col2 = st.columns(2)
            with col1:
                x_var = st.selectbox(
                    "Select X Variable",
                    ["Salinity [psu]", "Temperature [ITS90,°C]", "Oxygen [ml/l]","Flourescence [mg/m^3]"],
                    index=0,
                )
            with col2:
                y_var = st.selectbox(
                    "Select Y Variable",
                    ["Temperature [ITS90,°C]", "Salinity [psu]", "Oxygen [ml/l]","Flourescence [mg/m^3]"],
                    index=0,
                )

            add_regression = st.radio(
                "Add Trend (Linear Regression) Line?", ("No", "Yes")
            )

            fig_ts = go.Figure()

            for season in selected_season:
                for station in filtered_data["Grid"].unique():
                    for year in selected_year:
                        TS_data = filtered_data[
                            (filtered_data["Grid"] == station)
                            & (filtered_data["season"] == season)
                            & (filtered_data["datetime"].dt.year == year)
                        ]
                        if not TS_data.empty:
                            group_name = f"{station} {season} {year}"

                            fig_ts.add_trace(
                                go.Scatter(
                                    x=TS_data[x_var],
                                    y=TS_data[y_var],
                                    mode="markers",
                                    name=group_name,
                                    legendgroup=group_name,
                                )
                            )

                            if add_regression == "Yes":
                                X = TS_data[x_var]
                                y = TS_data[y_var]
                                X = sm.add_constant(X)
                                model = sm.OLS(y, X).fit()
                                X_pred = np.linspace(
                                    X[x_var].min(), X[x_var].max(), 100
                                )
                                X_pred = sm.add_constant(X_pred)
                                y_pred = model.predict(X_pred)

                                equation = f"y = {model.params[1]:.3f}x + {model.params[0]:.3f}"
                                r_squared = f"R² = {model.rsquared:.3f}"

                                fig_ts.add_trace(
                                    go.Scatter(
                                        x=X_pred[:, 1],
                                        y=y_pred,
                                        mode="lines",
                                        name=f"Regression {group_name}",
                                        hovertemplate=f"{equation}<br>{r_squared}<br>Station: {station}, Season: {season}, Year: {year}",
                                        showlegend=False,
                                        legendgroup=group_name,
                                    )
                                )

            fig_ts.update_layout(
                title=f"Regression Plot: {x_var} vs {y_var}",
                yaxis_title=y_var,
                xaxis_title=x_var,
                legend_title="Station, Season, Year",
            )

            st.plotly_chart(fig_ts, config=config_figure)

        elif analysis_option == "Box Plot":
            st.header("Box Plot")
            variable = st.selectbox(
                "Select Variable",
                ["Temperature [ITS90,°C]", "Salinity [psu]", "Oxygen [ml/l]","Flourescence [mg/m^3]"],
                index=0,
            )
            fig_stats = go.Figure()
            for season in selected_season:
                for station in filtered_data["Grid"].unique():
                    for year in selected_year:
                        Stats_data = filtered_data[
                            (filtered_data["Grid"] == station)
                            & (filtered_data["season"] == season)
                            & (filtered_data["datetime"].dt.year == year)
                        ]
                        if not Stats_data.empty:  # Corrected this line
                            fig_stats.add_trace(
                                go.Box(
                                    y=Stats_data[variable],
                                    x=[f"{station} {season} {year}"] * len(Stats_data),
                                    name=f"{station} {season} {year}",
                                )
                            )

            fig_stats.update_layout(
                xaxis_title="Station, Season, Year",
                yaxis_title=variable,
                legend_title="Station, Season, Year",
                boxmode="group",
            )

            st.plotly_chart(fig_stats, config=config_figure)

        elif analysis_option == "Correlation Heatmap":
            st.header("Correlation Heatmap")
            selected_station = st.selectbox(
                "Select Station for Correlation Heatmap", data["Grid"].unique()
            )
            st.write(" ")
            fig_corr = generate_correlation_heatmap(selected_station, data)

            st.plotly_chart(fig_corr, config=config_figure)
    else:
        st.warning("Please select at least one grid to visualize the data.")
