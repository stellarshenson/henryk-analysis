import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import json
from wordcloud import WordCloud

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
    try:
        with open(mapping_file, 'r') as file:
            mappings = json.load(file)
        return mappings
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {mapping_file}: {e}")
        return {}


def create_reverse_mapping(mappings):
    """
    Create a reverse mapping from specific categories to broader categories.

    Parameters:
    -----------
    mappings : dict
        The dictionary containing the broader to specific categories mappings.

    Returns:
    --------
    dict
        The dictionary containing the specific to broader categories mappings.
    """
    reverse_mapping = {}
    for broad_category, specific_categories in mappings.items():
        for specific_category in specific_categories:
            reverse_mapping[specific_category] = broad_category
    return reverse_mapping

def map_categorical_values(df, column, mapping_file):
    """
    Map categorical values to broader categories.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column to map.
    mapping_file : str
        Path to the JSON file containing the mappings.

    Returns:
    --------
    pd.DataFrame
        The DataFrame with the mapped column.
    """
    mappings = load_mappings(mapping_file)
    reverse_mapping = create_reverse_mapping(mappings)
    df[column] = df[column].map(reverse_mapping).fillna(df[column])
    return df


def translate_words(text, mappings):
    """
    Translate words in a text string using the provided mappings.

    Parameters:
    -----------
    text : str
        The text string containing words to translate.
    mappings : dict
        The dictionary containing the word mappings.

    Returns:
    --------
    str
        The translated text string.
    """
    words = text.split(',')
    translated_words = [mappings.get(word.strip(), word) for word in words]
    return ' '.join(translated_words)


def plot_categorical_histogram(df, column, mapping_file=None, title=None, xlabel=None, ylabel='Frequency', figsize=(14, 6), palette='coolwarm'):
    """
    Plots a histogram for a categorical column in the given DataFrame using Matplotlib and Seaborn.

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
    figsize : tuple, optional
        The size of the figure. Defaults to (12, 8).
    palette : str, optional
        The color palette to use for the plot. Defaults to 'coolwarm'.

    Returns:
    --------
    None
    """
    # Load mappings if provided
    mappings = load_mappings(mapping_file) if mapping_file else None

    # Apply mappings if available
    if mappings:
        df[column] = df[column].map(mappings).fillna(df[column])
        mapped_title = mappings.get(column, column)
        xlabel = mappings.get(column, xlabel if xlabel else column)
        ylabel = mappings.get('Frequency', ylabel)
    else:
        mapped_title = column

    # Use provided title or mapped title
    plot_title = title if title else mapped_title

    # Set up the figure
    plt.figure(figsize=figsize)
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['figure.facecolor'] = 'white'

    # Plot the histogram
    ax = sns.countplot(data=df, y=column, palette=palette, order=df[column].value_counts().index)

    # Add percentages
    total = len(df[column])
    for p in ax.patches:
        # percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        percentage = f'{100 * p.get_width() / total:.1f}%\n{p.get_width():.0f}'
        x = p.get_width() + 0.02 * total  # Adjust to prevent overlapping with the border
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y), ha='left', va='center', fontsize=12)

    # Set plot labels and title
    plt.title(plot_title, fontsize=18, pad=20)
    plt.xlabel(ylabel, fontsize=14)  # Correct the xlabel
    plt.ylabel(xlabel, fontsize=14)  # Correct the ylabel

    # Adjust x-axis limit for padding
    max_width = max([p.get_width() for p in ax.patches])
    plt.xlim(0, max_width * 1.25)
    
    # Add grid for better readability
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Display the plot
    plt.show()


def generate_word_cloud(df, column, mapping_file=None, title=None, figsize=(14, 6), background_color='white'):
    """
    Generate a word cloud image from the comma-separated values in the specified column.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column with comma-separated values.
    mapping_file : str, optional
        Path to the JSON file containing the mappings. Defaults to None.
    title : str, optional
        The title of the word cloud plot. Defaults to None.
    figsize : tuple, optional
        The size of the figure (width, height) in inches. Defaults to (10, 5).
    background_color : str, optional
        The background color of the word cloud image. Defaults to 'white'.

    Returns:
    --------
    None
    """
    # Load mappings if provided
    mappings = load_mappings(mapping_file) if mapping_file else {}

    # Concatenate all the values in the column into a single string
    all_topics = ','.join(df[column].dropna())

    # Translate the words using the mappings
    translated_topics = translate_words(all_topics, mappings)

    # Generate the word cloud
    wordcloud = WordCloud(width=figsize[0]*100, height=figsize[1]*100, background_color=background_color).generate(translated_topics)

    # Plot the word cloud
    plt.figure(figsize=figsize)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    if title:
        plt.title(title, fontsize=16)
    plt.show()

def plot_binary_columns_histogram(df, columns, mapping_file, title='Histogram of Binary Columns', figsize=(12, 8), palette='coolwarm'):
    """
    Plot a histogram for binary columns showing the number of recordings where the value is 1.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the data.
    columns : list
        The list of column names to plot.
    mapping_file : str
        Path to the JSON file containing the column name mappings.
    title : str, optional
        The title of the plot. Defaults to 'Histogram of Binary Columns'.
    figsize : tuple, optional
        The size of the figure. Defaults to (12, 8).
    palette : str, optional
        The color palette to use for the plot. Defaults to 'coolwarm'.

    Returns:
    --------
    None
    """
    # Load mappings
    mappings = load_mappings(mapping_file)

    # Calculate the counts and percentages
    counts = {col: df[col].sum() for col in columns}
    total_recordings = len(df)
    percentages = {col: (df[col].mean() * 100) for col in columns}
    mapped_labels = [mappings.get(col, col) for col in columns]

    # Prepare the data for plotting
    plot_data = pd.DataFrame({
        'Column': mapped_labels,
        'Count': [counts[col] for col in columns],
        'Percentage': [percentages[col] for col in columns]
    })

    # Set up the figure
    plt.figure(figsize=figsize)
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['figure.facecolor'] = 'white'

    # Plot the histogram
    ax = sns.barplot(x='Count', y='Column', data=plot_data, palette=palette)

    # Add counts and percentages on the bars
    for index, row in plot_data.iterrows():
        ax.text(row['Count'] + 0.5, index, f'{row["Percentage"]:.1f}%\n{row["Count"]:.0f}', color='black', va="center", fontsize=12)
        # ax.text(row['Count'] + 0.5, index, f'{row["Count"]} ({row["Percentage"]:.1f}%)', color='black', va="center", fontsize=12)

    # Set plot labels and title
    plt.title(title, fontsize=18, pad=20)
    plt.xlabel('Number of Recordings', fontsize=14)
    plt.ylabel('')

    # Add grid
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Display the plot
    plt.show()


# EOF