import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os

# Inicializa la app de Dash
app = dash.Dash(__name__)

# Ruta del archivo CSV con las predicciones
predictions_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'predictions.csv')

# Función para cargar las predicciones desde el archivo CSV
def load_predictions():
    if os.path.exists(predictions_file):
        return pd.read_csv(predictions_file)
    else:
        return pd.DataFrame(columns=["timestamp", "input_data", "prediction"])

# Cargar las predicciones inicialmente
df_predictions = load_predictions()

# Gráfico de distribución de predicciones (0 y 1)
def generate_graph():
    df_predictions = load_predictions()
    if df_predictions.empty:
        return px.histogram(df_predictions, x="prediction", title="Distribución de Predicciones", labels={"prediction": "Resultado (0 o 1)"})
    else:
        return px.histogram(df_predictions, x="prediction", title="Distribución de Predicciones", labels={"prediction": "Resultado (0 o 1)"})

# Diseño del Dashboard
app.layout = html.Div(children=[
    html.H1("Dashboard de Predicciones"),
    
    # Mostrar un gráfico de distribución
    dcc.Graph(
        id='prediction-distribution',
        figure=generate_graph()
    ),
    
    # Tabla con las predicciones recientes
    html.H3("Predicciones Recientes"),
    html.Table(id='prediction-table')
])

# Callback para actualizar el gráfico y la tabla
@app.callback(
    [Output('prediction-distribution', 'figure'),
     Output('prediction-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Cargar las predicciones
    df_predictions = load_predictions()

    # Actualizar gráfico
    fig = generate_graph()

    # Crear la tabla de predicciones
    if not df_predictions.empty:
        table_header = [html.Th(col) for col in df_predictions.columns]
        table_body = [
            html.Tr([html.Td(df_predictions.iloc[i][col]) for col in df_predictions.columns])
            for i in range(min(len(df_predictions), 10))  # Muestra las 10 últimas predicciones
        ]
        table = html.Table([html.Thead(table_header), html.Tbody(table_body)])
    else:
        table = html.Div("No hay predicciones disponibles.")

    return fig, table

# Componente Intervalo para actualizar el dashboard cada 5 segundos
app.layout.children.append(
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # Actualizar cada 5 segundos
        n_intervals=0
    )
)

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)


