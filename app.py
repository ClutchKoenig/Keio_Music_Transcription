from flask import Flask, request, send_file
from flask_cors import CORS
import tempfile
import subprocess
from io import BytesIO
import os

# Long-running imports
import tensorflow as tf

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files.get('audio')
    format = request.form.get('format')  # 'midi' or 'pdf'

    if not file:
        return {'error': 'No file uploaded'}, 400

    # Créer un fichier temporaire pour l’entrée
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
        file.save(tmp_input.name)
        input_path = tmp_input.name

    # Créer un fichier temporaire pour la sortie
    output_ext = 'mid' if format == 'midi' else 'pdf'
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_ext}") as tmp_output:
        output_path = tmp_output.name

    try:
        subprocess.run([
            "python3", "src/run_model.py",
            "--input", input_path,
            "--output", output_path,
            "--format", format
        ], check=True)

        # Lire le fichier de sortie
        with open(output_path, 'rb') as f:
            file_data = BytesIO(f.read())

    except subprocess.CalledProcessError:
        return {'error': 'Processing failed'}, 500

    finally:
        # Nettoyage des fichiers temporaires
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=f"conversion.{output_ext}",
        mimetype='application/octet-stream'
    )

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_file(f'static/{path}')

if __name__ == '__main__':
    app.run(debug=True)
