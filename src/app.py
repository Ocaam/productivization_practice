import os
import pickle
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import csv

# Inicializa la aplicación Flask
app = Flask(__name__)

# Ruta para servir los archivos HTML
base_folder = os.path.dirname(os.path.abspath(__file__))  # Carpeta 'src'
web_folder = os.path.join(base_folder, '..', 'web')  # Carpeta 'web'

# Ruta del modelo
model_path = os.path.join(base_folder, '../models/trained_model.pkl')
if not os.path.exists(model_path):
    raise FileNotFoundError(f"The file {model_path} was not found.")

with open(model_path, 'rb') as file:
    model = pickle.load(file)

# Ruta para servir el archivo index.html
@app.route('/')
def home():
    return send_from_directory(web_folder, 'index.html')

# Función para registrar las predicciones en un archivo CSV
def log_prediction(input_data, prediction):
    # Preparamos los datos que vamos a guardar
    data = {
        "timestamp": datetime.now().isoformat(),
        "input_data": str(input_data),
        "prediction": prediction
    }

    # Ruta de la carpeta 'data' donde se guardará el archivo CSV
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    # Asegurarnos de que la carpeta 'data' exista
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print("Carpeta 'data' creada.")
    
    # Ruta del archivo CSV donde se guardarán las predicciones
    file_path = os.path.join(data_folder, 'predictions.csv')

    # Comprobamos si el archivo ya existe para determinar si escribimos los encabezados
    file_exists = os.path.exists(file_path)

    # Guardar en formato CSV
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "input_data", "prediction"])
        
        # Si el archivo no existe, escribir encabezados
        if not file_exists:
            writer.writeheader()

        writer.writerow(data)
        print(f"Predicción guardada: {data}")

# Ruta para recibir las predicciones
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_data = pd.DataFrame([data])

        # Asegurarse de que las columnas coincidan con las del modelo
        required_columns = [
            'EXT_SOURCE_1', 'OCCUPATION_TYPE', 'EXT_SOURCE_3', 'AMT_REQ_CREDIT_BUREAU_QRT',
            'DEF_30_CNT_SOCIAL_CIRCLE', 'EXT_SOURCE_2', 'AMT_GOODS_PRICE', 'AMT_ANNUITY',
            'DAYS_LAST_PHONE_CHANGE', 'CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_DOCUMENT_3',
            'FLAG_DOCUMENT_16', 'AMT_CREDIT', 'REG_CITY_NOT_LIVE_CITY', 
            'REGION_RATING_CLIENT_W_CITY', 'ORGANIZATION_TYPE', 'DAYS_ID_PUBLISH', 
            'NAME_EDUCATION_TYPE', 'FLAG_WORK_PHONE'
        ]
        input_data = input_data[required_columns]

        # Realizar la predicción
        prediction = model.predict(input_data)

        # Registrar la predicción
        log_prediction(input_data, prediction[0])

        # Responder con la predicción
        response = {'prediction': int(prediction[0])}
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


