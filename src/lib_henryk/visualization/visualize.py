import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import pandas as pd
import plotly.express as px
import json

def load_mappings(mapping_file):
    """
    Load mappings from a JSON file.

    Parameters:
    -----------
    mapping_file : str
        Path to the JSON file containing the mappings.

    Returns:
    --------
    dict
        The dictionary containing the mappings.
    """
    with open(mapping_file, 'r') as file:
        mappings = json.load(file)
    return mappings

def plot_categorical_histogram(df, column, mapping_file=None, title=None, xlabel=None, ylabel='Frequency', palette='Viridis'):
    """
    Plots a histogram for a categorical column in the given DataFrame using Plotly.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column to plot.
    mapping_file : str, optional
        Path to the JSON file containing the mappings. Defaults to None.
    title : str, optional
        The title of the plot. Defaults to the column name.
    xlabel : str, optional
        The label for the x-axis. Defaults to the column name.
    ylabel : str, optional
        The label for the y-axis. Defaults to 'Frequency'.
    palette : str, optional
        The color palette to use for the plot. Defaults to 'Viridis'.

    Returns:
    --------
    None
    """
    # Load mappings if provided
    mappings = load_mappings(mapping_file) if mapping_file else None

    # Apply mappings if available
    if mappings:
        df[column] = df[column].map(mappings).fillna(df[column])

    # Generate the plot
    fig = px.histogram(df, x=column, color=column, title=title if title else column, color_discrete_sequence=px.colors.sequential.Viridis)

    # Update layout for better visuals
    fig.update_layout(
        xaxis_title=xlabel if xlabel else column,
        yaxis_title=ylabel,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        title_font=dict(size=20, color='black', family='Arial'),
        xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='lightgray'),
        autosize=True,
        width=1200,
        height=800,
    )

    # Show percentages on the bars
    total = len(df)
    for trace in fig.data:
        if trace.y is not None:
            trace.text = [f'{y} ({100 * y / total:.1f}%)' for y in trace.y]
            trace.textposition = 'outside'

    # Display the plot
    fig.show()


def load_mappings(mapping_file):
    """
    Load mappings from a JSON file.

    Parameters:
    -----------
    mapping_file : str
        Path to the JSON file containing the mappings.

    Returns:
    --------
    dict
        The dictionary containing the mappings.
    """
    with open(mapping_file, 'r') as file:
        mappings = json.load(file)
    return mappings


# EOF