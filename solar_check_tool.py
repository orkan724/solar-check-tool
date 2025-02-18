from flask import Flask, request, send_file
import pandas as pd
import os
import requests
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Neuer MaStR API Key
MASTR_API_KEY = "CoqOTwRMhw3PH3XwrAIxDwmxM6JEmNG2B4uITjBMEFEtnAYA0wF12WNZW4WmLNv79q8pZJHeyMnRP7H4xitQmrHfKii2cieAdqgdE8kior57EAsNSriBOVUTv5mUDF7wsEX1ipgOeyEh3o2BD8gj4RI7ZVeZopzLNXUfbpu4cGHoruJllzg/WL3SMvPLV7R8yUPKKBdGjSPYa89Ra0Q6/xDql2ew/IfobcZZzCmA5LszZ2APkv+lcNvY+52IGIYy3jc4gzwkG9sfPTQb/3iR0qJVsbGK+oaJ8MMUuukGPqjA+2QjSAMGCBkPBYLw6Gn1vQL2w8d5/R5BfqnyyOjh1K774VEh4aHpByn26vRGCbHUfDUmjJL1MkpwtGhD3pkrX+vy0WYBoF576WQFV1f45uNd7a9xaatUMitDPFDxhNov/2Xcfc44y146h3BjG5YCZmAvdQVW6S6E4JneuuNbLpRdBOdNrLbHn6J9E2peGW4eKk+JORqNPF/Ko3JQl0SX9ehGTax3Mqv/GtSVdMxxTyAoLVI="

# Funktion zur Überprüfung der Solaranlage mit Fehlerbehandlung
def check_solar_installation(address):
    url = "https://www.marktstammdatenregister.de/api/solaranlage/search"
    headers = {"Authorization": f"Bearer {MASTR_API_KEY}", "Content-Type": "application/json"}
    params = {"address": address}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        if response.text.strip():
            data = response.json()
            return "Ja" if data.get("results") else "Nein"
        else:
            return "Keine Antwort von API"

    except requests.exceptions.RequestException as e:
        return f"API-Fehler: {str(e)}"

    except requests.exceptions.JSONDecodeError:
        return "Ungültige JSON-Antwort"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)

            if not {'Straße', 'PLZ', 'Ort'}.issubset(df.columns):
                return "Fehlende Spalten: Die Datei muss 'Straße', 'PLZ', 'Ort' enthalten!"

            df['Hat eine Solaranlage'] = df.apply(
                lambda row: check_solar_installation(f"{row['Straße']}, {row['PLZ']} {row['Ort']}"), axis=1
            )

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
