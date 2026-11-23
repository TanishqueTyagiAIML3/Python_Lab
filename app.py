import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1. Load Dataset
url = 'https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv'
df = pd.read_csv(url)

print("Dataset Loaded")
print("Shape:", df.shape)
print("Columns:", df.columns)

# 2. Data Clean
required_colum = ['latitude', 'longitude', 'price', 'minimum_nights']
missing = [c for c in required_colum if c not in df.columns]
if missing:
    raise ValueError("Missing columns: {}".format(missing))

for col in required_colum:
    if col == 'price':
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r'[^\d.]', '', regex=True),
            errors='coerce'
        )
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=required_colum)
df = df[df['latitude'].between(-90, 90) & df['longitude'].between(-180, 180)]

print("Clean Dataset")
print(df.head())

if df.empty:
    raise ValueError("Empty Dataset")

# 3. Initialize Dash App
app = Dash(__name__)

max_price = max(1000, int(df['price'].max()))

app.layout = html.Div(
    children=[
        html.H1(children='Airbnb Listings Map', style={'textAlign': 'center'}),
        html.H3("Select Minimum Nights"),
        dcc.Slider(
            id='night-slider',
            min=1,
            max=30,
            step=1,
            value=3,
            marks={i: str(i) for i in range(1, 31, 5)}
        ),
        html.Br(),
        html.H3("Select Price Range"),
        dcc.RangeSlider(
            id='price-slider',
            min=0,
            max=max_price,
            value=[0, min(2500, max_price)],
            step=100,
            marks=None,
            tooltip={'placement': 'bottom', 'always_visible': True}
        ),
        html.Br(),
        html.H4(id='count', style={'textAlign': 'center'}),
        dcc.Graph(id='airbnb-map', style={'height': '700px'})
    ],
    style={'padding': '30px'}
)

# 4. Callback
@app.callback(
    Output('airbnb-map', 'figure'),
    Output('count', 'children'),
    Input('night-slider', 'value'),
    Input('price-slider', 'value')
)
def update_graph(nights, price_range):
    dff = df[
        (df['minimum_nights'] >= nights) &
        (df['price'] >= price_range[0]) &
        (df['price'] <= price_range[1])
    ]
    print(f"Filtered rows: {len(dff)}")

    fig = px.scatter_geo(
        dff,
        lat='latitude',
        lon='longitude',
        color='price',
        hover_name='name' if 'name' in dff.columns else None,
        hover_data=['price', 'minimum_nights'],
        title='Airbnb Listings'
    )

    # Fixed: showscountries -> showcountries
    fig.update_geos(showcountries=True, fitbounds="locations")

    return fig, f"Total Filtered Listings: {len(dff)}"

# 5. Run App
if __name__ == '__main__':
    app.run(debug=True, port=5000)