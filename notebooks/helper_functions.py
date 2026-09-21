import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

metro_city_dictionary = {
    "Mumbai": 1,
    "Bangalore": 1,
    "Chennai": 1,
    "New Delhi": 1,
    "Pune": 0,
    "Nagpur": 0,
    "Kochi": 0,
    "Trivandrum": 0,
    "Mysore": 0,
    "Coimbatore": 0,
    "Ahmedabad": 0,
    "Surat": 0 
}

def plot_bar_chart(
        df: pd.DataFrame, 
        x_col: str, 
        y_col: str, 
        title: str, 
        x_label: str, 
        y_label: str, 
        x_tick_rotation: int = 0,
        horizontal: bool = False
    ):
    fig, ax = plt.subplots(figsize = (12, 5))

    if horizontal:
        sns.barplot(x = y_col, y = x_col, data = df, ax = ax)
    else: 
        sns.barplot(x = x_col, y = y_col, data = df, ax = ax)
    ax.set_title(title)
    if horizontal:
        ax.set_ylabel(x_label)
        ax.set_xlabel(y_label)
    else:
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    if not horizontal:
        ax.tick_params(axis = 'x', rotation = x_tick_rotation)
    plt.tight_layout()

    return fig

def plot_scatter_plot(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str
):
    fig, ax = plt.subplots(figsize = (12, 5))

    sns.scatterplot(x = x_col, y = y_col, data = df, ax = ax)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    plt.tight_layout()

    return fig

def normalize_score(series):
    return ((series - series.min()) / (series.max() - series.min()) * 100).fillna(0)



