from flask import Flask, request, send_file, session, redirect, url_for
import pandas as pd
import os
import requests
import sqlite3
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Funktion zur Überprüfung der Solaranlage (Daten von Marktstammdatenregister abrufen)
def check_solar_installation(address):
    url = "https://www.marktstammdatenregister.de/api/solaranlage/search"
    headers = {"Authorization": "Bearer YOUR_MASTR_API_KEY", "Content-Type": "application/json"}
    params = {"address": address}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return "Ja" if data.get("results") else "Nein"
    else:
        return "Fehler"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            
            if not {'Straße', 'PLZ', 'Ort'}.issubset(df.columns):
                return "Fehlende Spalten: Die Datei muss 'Straße', 'PLZ', 'Ort' enthalten!"
            
            df['Hat eine Solaranlage'] = df.apply(lambda row: check_solar_installation(f"{row['Straße']}, {row['PLZ']} {row['Ort']}"), axis=1)
            
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            return send_file(output, as_attachment=True, download_name="solar_check_result.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    return '''
        <h1>Solar Check Tool</h1>
        <form action="" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
