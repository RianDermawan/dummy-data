from flask import Flask
from flask import jsonify
from datetime import datetime
import json
import pandas as pd
import numpy as np

app = Flask(__name__)

def generate_dummy_data(column_names, lower_bound, upper_bound):
    today = datetime.today().strftime('%d-%m-%Y')
    data = pd.DataFrame({'Tanggal': [today]})

    for col in column_names:
        data[col] = np.random.randint(lower_bound, upper_bound)
    
    data[column_names] *= 1000
    
    json_data = data.to_json(orient='records')
    
    return json_data

@app.route('/kereta-penumpang/antar-kota')
def antar_kota():
    dummy_json = generate_dummy_data(['Ekonomi', 'Bisnis', 'Eksekutif'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/commuter-line')
def commuter_line():
    dummy_json = generate_dummy_data(['Jabodetabek', 'Yogyakarta'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/bandara')
def bandara():
    dummy_json = generate_dummy_data(['Medan', 'Yogyakarta'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/wisata')
def wisata():
    dummy_json = generate_dummy_data(['nusantara','sumatera','bali','toraja','jawa','imperial','retro','priority'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/cargo')
def cargo():
    dummy_json = generate_dummy_data(['Angkutan Retail', 'Angkutan Korporat'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/logistik')
def logistik():
    dummy_json = generate_dummy_data(['Express', 'Plus', 'Pro'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/barang-bagasi')
def barang_bagasi():
    dummy_json = generate_dummy_data(['Ekonomi', 'Bisnis', 'Eksekutif'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

app.run()