import pandas as pd
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load the dataset
file_path = 'E-Commerce_Data.csv'  # Replace with the actual path to your CSV file
df = pd.read_csv(file_path)

# Clean column names: remove any leading/trailing spaces and standardize to lowercase
df.columns = df.columns.str.strip().str.lower()

# Convert 'Order Date' to datetime, handle errors, and create 'YearMonth'
df['order date'] = pd.to_datetime(df['order date'], dayfirst=True, errors='coerce')  # Ensure column names match
df['yearmonth'] = df['order date'].dt.to_period('M')

# Drop rows with invalid dates
df_cleaned = df.dropna(subset=['order date'])

# Convert 'sales' column to numeric
if 'sales' in df_cleaned.columns:
    df_cleaned['sales'] = pd.to_numeric(df_cleaned['sales'], errors='coerce')
else:
    raise KeyError("'Sales' column is missing from the dataset.")

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("E-Commerce Sales Dashboard", style={'text-align': 'center', 'background-color':'black', 'color':'white'}),

    # Dropdown for category selection
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': c, 'value': c} for c in df_cleaned['product category'].unique()],
        value=df_cleaned['product category'].unique()[0],  # Default value
        clearable=False
    ),

    #Summary Statistics
    html.Div(id='summary-metrics', style={'display': 'flex', 'justify-content': 'space-around'}),

    # Graph for sales trend
    dcc.Graph(id='sales-trend-graph'),

    # Graph for shipping days histogram
    dcc.Graph(id='shipping-days-histogram')
])

# Define the callback to update graphs based on the selected category
@app.callback(
    [Output('sales-trend-graph', 'figure'),
     Output('shipping-days-histogram', 'figure'),
     Output('summary-metrics', 'children')],
    [Input('category-dropdown', 'value')]
)
def update_dashboard(selected_category):
    # Filter data based on the selected category
    filtered_data = df_cleaned[df_cleaned['product category'] == selected_category]

      # Create a line chart for sales trends
    sales_trend = filtered_data.groupby('YearMonth').sum().reset_index()
    fig1 = px.line(sales_trend, x='YearMonth', y='Sales', title=f'Sales Trend for {selected_category}', 
                   labels={'YearMonth': 'Month-Year', 'Sales': 'Total Sales'})

    # Create a histogram for shipping days
    fig2 = px.histogram(filtered_data, x='ShippingDays', nbins=20, title='Distribution of Shipping Days',
                        labels={'ShippingDays': 'Number of Shipping Days'})

    # Calculate summary metrics
    total_sales = filtered_data['Sales'].sum()
    avg_shipping_days = filtered_data['ShippingDays'].mean()
    num_orders = filtered_data.shape[0]
    
    summary = [
        html.Div(f"Total Sales: ${total_sales:,.2f}", style={'fontSize': 24}),
        html.Div(f"Average Shipping Days: {avg_shipping_days:.2f}", style={'fontSize': 24}),
        html.Div(f"Number of Orders: {num_orders}", style={'fontSize': 24})
    ]
    return fig1, fig2, summary

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
