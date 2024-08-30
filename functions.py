import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import streamlit as st

def generate_correlation_heatmap(Correlation_station, data):
    if not Correlation_station:
        # Create an empty heatmap figure
        fig = go.Figure()
        fig.update_layout(title="No station selected")
        return fig

    # Extract the station from the list
    station = (
        Correlation_station[-1]
        if isinstance(Correlation_station, list)
        else Correlation_station
    )

    # Filter data for the selected station
    station_filter = data["Grid"] == station
    filtered_data = data[station_filter]

    # Define the list of specific variables to include
    variables = [
        "Pressure [db]",
        "Temperature [ITS90,°C]",
        "Salinity [psu]",
        "Oxygen [ml/l]",
        "Flourescence [mg/m^3]"
    ]

    # Ensure the variables exist in the filtered data
    available_variables = [var for var in variables if var in filtered_data.columns]
    
    # Select only the numeric data for the available variables
    numeric_data = filtered_data[available_variables].select_dtypes(include=[np.number])
    
    # Calculate the correlation matrix
    corr_matrix = numeric_data.corr()
    
    # Create a mask for the upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Apply the mask to the correlation matrix, setting upper triangle values to NaN
    masked_corr_matrix = corr_matrix.mask(mask)
    
    # Drop rows and columns where all values are NaN
    masked_corr_matrix = masked_corr_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')

    # Generate a heatmap from the masked correlation matrix
    fig = px.imshow(
        masked_corr_matrix,
        labels=dict(color="Correlation"),
        zmin=-1,
        zmax=1,
        x=masked_corr_matrix.columns,
        y=masked_corr_matrix.index,
        text_auto=True,  # Automatically add text on each cell
        aspect="auto",
        color_continuous_scale="RdBu_r",  # Set color scale to blue-white-red
        template="simple_white"
    )
    fig.update_layout(
        title=f"Correlation Heatmap for {station}",
        #margin={"r": 0, "t": 50, "l": 0, "b": 0},
        margin=dict(l=150, r=20, t=40, b=40),  # Adjust margins as needed
        plot_bgcolor="white",
        hovermode=False
    )
    # Update tick font size for both axes
    fig.update_xaxes(tickfont=dict(size=18),tickcolor="black")
    fig.update_yaxes(tickfont=dict(size=18),tickcolor="black")
    
    return fig


#Configuration for high-resolution plot export
config_figure = {
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        'filename': 'IEP_Figures',
        'height': 1000,
        'width': 1000,
        'scale': 4  # Multiply title/legend/axis/canvas sizes by this factor
    }
}
