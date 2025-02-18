import os
import logging
import requests
import pandas as pd
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

# Logging einrichten
logging.basicConfig(filename="api_debug.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# API-Einstellungen
API_URL = "https://www.marktstammdatenregister.de/api/check"
API_KEY = "CoqOTwRMhw3PH3XwrAIxDwmxM6JEmNG2B4uITjBMEFEtnAYA0wF12WNZW4WmLNv79q8pZJHeyMnRP7H4xitQmrHfKii2cieAdqgdE8kior57EAsNSriBOVUTv5mUDF7wsEX1ipgOeyEh3o2BD8gj4RI7ZVeZopzLNXUfbpu4cGHoruJllzg/WL3SMvPLV7R8yUPKKBdGjSPYa89Ra0Q6/xDql2ew/IfobcZZzCmA5LszZ2APkv+lcNvY+52IGIYy3jc4gzwkG9sfPTQb/3iR0qJVsbGK+oaJ8MMUuukGPqjA+2QjSAMGCBkPBYLw6Gn1vQL2w8d5/R5BfqnyyOjh1K774VEh4aHpByn26vRGCbHUfDUmjJL1MkpwtGhD3pkrX+vy0WYBoF576WQFV1f45uNd7a9xaatUMitDPFDxhNov/2Xcfc44y146h3BjG5YCZmAvdQVW6S6E4JneuuNbLpRdBOdNrLbHn6J9E2peGW4eKk+JORqNPF/Ko3JQl0SX9ehGTax3Mqv/GtSVdMxxTyAoLVI="

# Funktion zur Überprüfung der Solaranlage
def check_solar_installation(address):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"address": address}
    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        if "text/html" in response.headers.get("Content-Type", ""):
            logging.error(f"Fehlermeldung erhalten für {address}: {response.text}")
            return "Fehlerhafte API-Antwort"
        
        data = response.json()
        return data.get("solar_installation", "Keine Daten")
    except requests.exceptions.RequestException as e:
        logging.error(f"Fehler bei API-Anfrage für {address}: {e}")
        return "API-Fehler"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "Keine Datei hochgeladen"
        
        df = pd.read_excel(file)
        
        if not all(col in df.columns for col in ["Straße", "PLZ", "Ort"]):
            return "Fehlende Spalten in der Datei"
        
        df["Hat eine Solaranlage"] = df.apply(lambda row: check_solar_installation(f"{row['Straße']}, {row['PLZ']} {row['Ort']}") if pd.notnull(row["Straße"]) else "Ungültige Adresse", axis=1)
        
        output_filename = "output.xlsx"
        df.to_excel(output_filename, index=False)
        return send_file(output_filename, as_attachment=True)
    
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
