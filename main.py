from flask import Flask
from flask import jsonify
from datetime import datetime
import json
import pandas as pd
import numpy as np

app = Flask(__name__)

def generate_dummy_data(column_names, lower_bound, upper_bound):
    today = datetime.today().strftime('%Y-%m-%d')
    data = pd.DataFrame({'tanggal': [today]})

    for col in column_names:
        data[col] = np.random.randint(lower_bound, upper_bound)
    
    data[column_names] *= 1000
    
    json_data = data.to_json(orient='records')
    
    return json_data

@app.route('/kereta-penumpang/antar-kota')
def antar_kota():
    dummy_json = generate_dummy_data(['ekonomi', 'bisnis', 'eksekutif'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/commuter-line')
def commuter_line():
    dummy_json = generate_dummy_data(['jabodetabek', 'yogyakarta'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/bandara')
def bandara():
    dummy_json = generate_dummy_data(['medan', 'yogyakarta'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-penumpang/wisata')
def wisata():
    dummy_json = generate_dummy_data(['nusantara','sumatera','bali','toraja','jawa','imperial','retro','priority'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/cargo')
def cargo():
    dummy_json = generate_dummy_data(['angkutan_retail', 'angkutan_korporat'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/logistik')
def logistik():
    dummy_json = generate_dummy_data(['express', 'plus', 'pro'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/kereta-barang/barang-bagasi')
def barang_bagasi():
    dummy_json = generate_dummy_data(['ekonomi', 'bisnis', 'eksekutif'], 100000, 1000000)
    return jsonify(json.loads(dummy_json))

@app.route('/sentimen-analisis')
def sentiment_analysis():
    import requests
    from bs4 import BeautifulSoup
    import time

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager

    def ambil_data(url):
        urlx = requests.get(url)
        isi_urlx = BeautifulSoup(urlx.content, 'html.parser')
        textx = isi_urlx.find_all('p')
        tanggal = isi_urlx.find('div', class_='text-cnn_grey text-sm mb-4').text
        
        full_text = ''
        for row in textx:
            full_text += row.text
            full_text += '\n\n'
        full_text_baru = full_text[:-2]
        full_text_baru = full_text_baru.replace('ADVERTISEMENT', '')
        full_text_baru = full_text_baru.replace('SCROLL TO CONTINUE WITH CONTENT', '')
        
        return full_text_baru, tanggal

    def ganti_bulan(input_kata):
        
        bulan_dict = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "Mei": "05",
        "Jun": "06",
        "Jul": "07",
        "Agu": "08",
        "Sep": "09",
        "Okt": "10",
        "Nov": "11",
        "Des": "12"
        }
        
        for bulan_lama, bulan_baru in bulan_dict.items():
            input_kata = input_kata.replace(bulan_lama, bulan_baru)

        return input_kata

    def get_crawl():
        keyword = 'kereta'
        url = f'https://www.cnnindonesia.com/search/?query={keyword}'
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        #geckodriver_path = '/home/mlflow/hackaton/geckodriver'
        #driver = webdriver.Firefox()
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, "lxml")
        urls = soup.find_all('a', class_='gap-4')

        judul = [urls[i].find('h2').text for i in range(len(urls))]
        url = [urls[i]['href'] for i in range(len(urls))]

        json_list = []
        for index, urlx in enumerate(url):
            try:
                hasil_json = {}
                data = ambil_data(urlx)
                hasil_data = data[0]

                hasil_tanggal = data[1]
                hasil_tanggal = hasil_tanggal[hasil_tanggal.find(',')+2:hasil_tanggal.rfind('WIB')-1]
                hasil_tanggal = ganti_bulan(hasil_tanggal) + ':00'
                hasil_tanggal_datetime = datetime.strptime(hasil_tanggal, '%d %m %Y %H:%M:%S')
                hasil_tanggal_fix = hasil_tanggal_datetime.strftime("%Y-%m-%d %H:%M:%S")

                waktu_ambil = datetime.now()
                waktu_ambil_fix = waktu_ambil.strftime("%Y-%m-%d %H:%M:%S")

                hasil_judul = judul[index]

                hasil_json['title'] = hasil_judul
                hasil_json['url'] = urlx
                hasil_json['content'] = hasil_data
                hasil_json['keyword'] = keyword
                hasil_json['published_at'] = hasil_tanggal_fix
                hasil_json['created_at'] = waktu_ambil_fix

                json_list.append(hasil_json)

                time.sleep(5)
                
            except:
                print(f'Url --> {urlx}\nKonten tidak bisa diambil')

        return pd.DataFrame(json_list)

    df = get_crawl()

    from transformers import pipeline
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    pretrained= "mdhugol/indonesia-bert-sentiment-classification"

    model = AutoModelForSequenceClassification.from_pretrained(pretrained)
    tokenizer = AutoTokenizer.from_pretrained(pretrained)

    sentiment_analysis = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    label_index = {'LABEL_0': 'positive', 'LABEL_1': 'neutral', 'LABEL_2': 'negative'}

    def analyze_sentiment(text):
        result = sentiment_analysis(text)
        status = label_index[result[0]['label']]
        score = result[0]['score']
        return status, score

    # Buat kolom baru untuk menyimpan hasil sentiment analysis
    df['sentiment_status'] = ""
    df['sentiment_score'] = ""

    # Loop melalui setiap baris di kolom 'text' dan terapkan fungsi analyze_sentiment
    for index, row in df.iterrows():
        text = row['content']
        try:
            status, score = analyze_sentiment(text)
            df.at[index, 'sentiment_status'] = status
            df.at[index, 'sentiment_score'] = score
        except:
            status, score = analyze_sentiment(text[1000])
            df.at[index, 'sentiment_status'] = status
            df.at[index, 'sentiment_score'] = score

    df_json = df.to_json(orient='records')
    return jsonify(json.loads(df_json))

app.run()