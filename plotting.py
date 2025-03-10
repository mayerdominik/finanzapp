import plotly.graph_objects as go
import pandas as pd
from preprocess import extend_missing_data
import plotly.express as px


def pie_chart(data, name_column, value_column, title):
    """
    Create a pie chart from the data. 
    
    Parameters:
    data (pd.DataFrame): The data to plot.
    name_column (str): The column containing the names.
    value_column (str): The column containing the values.
    title (str): The title of the pie chart.
    
    Returns:
    plotly.graph_objects.Figure: The pie chart.
    """
    # color all values of the same category the same
    fig = px.pie(data, names=name_column, values=value_column, title=title)
    return fig

def plot_stock_price(data, interval = 'd', show_missing_data=True):
    """
    Plot the stock price data in a line cahrt, optionally with missing data points highlighted in red.
    
    Parameters:
    data (pd.DataFrame): The stock price data.
    interval (str): The time interval of the data (d = day, h = hour, m = minute).
    show_missing_data (bool): Whether to show missing data points.
    """
    # Create a Plotly figure
    fig = go.Figure()

    if show_missing_data:
        data_reindexed = extend_missing_data(data, interval=interval)
        
        flag1 = False
        flag2 = False
        # identify missing data points by plotting dashed lines to the next available point
        # go row by row, for each line between two points, make it red when one of the rows has a missing entry at column 'Open'
        for i, row in data_reindexed.iterrows():
            if i != 0:
                if pd.isna(row['Open']):
                    show_legend = False
                    if flag1 == False:
                        show_legend = True
                        flag1 = True
                    name = 'Missing Data'
                    fig.add_trace(go.Scatter(x=[data_reindexed['index'].iloc[i - 1], data_reindexed['index'].iloc[i]], 
                                            y=[data_reindexed['Close_EUR'].iloc[i - 1], data_reindexed['Close_EUR'].iloc[i]], 
                                            mode='lines', name=name, line=dict(color='red', dash='dot'), showlegend=show_legend))
                else:
                    show_legend = False
                    if flag2 == False:
                        show_legend = True
                        flag2 = True
                    name = "Price in EUR"
                    fig.add_trace(go.Scatter(x=[data_reindexed['index'].iloc[i - 1], data_reindexed['index'].iloc[i]], 
                                            y=[data_reindexed['Close_EUR'].iloc[i - 1], data_reindexed['Close_EUR'].iloc[i]], 
                                            mode='lines', name=name, line=dict(color='blue'), showlegend=show_legend))

        
    else:
        fig.add_trace(go.Scatter(x=data.index, y=data['Close_EUR'], mode='lines', name="Price in EUR"))

    # Set chart title and labels
    fig.update_layout(
        title="Hourly Prices of Core MSCI World USD (Acc) ETF in EUR",
        xaxis_title="Time",
        yaxis_title="Price (EUR)",
        yaxis=dict(automargin=True)  # Auto-adjust y-axis limits based on data
    )

    return fig