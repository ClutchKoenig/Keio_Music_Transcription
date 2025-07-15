import os, re, tempfile, shutil, subprocess
from flask import Flask, request, send_file
from flask_cors import CORS
from io import BytesIO
from pyngrok import ngrok
from src.run_model import process_audio

app = Flask(__name__)
CORS(app)

@app.after_request
def add_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files.get('audio')
    format = request.form.get('format')  # 'midi' or 'pdf'

    if not file:
        return {'error': 'No file uploaded'}, 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
        file.save(tmp_input.name)
        input_path = tmp_input.name

    output_dir = tempfile.mkdtemp()

    try:
        process_audio(input_path, output_dir, format)

        # Rechercher le fichier généré
        ext = 'mid' if format == 'midi' else 'pdf'
        search_dir = os.path.join(output_dir, 'midi' if format == 'midi' else 'score')
        output_files = [f for f in os.listdir(search_dir) if f.endswith(f".{ext}")]
        if not output_files:
            return {'error': 'No output file found'}, 500

        output_path = os.path.join(search_dir, output_files[0])

        with open(output_path, 'rb') as f:
            file_data = BytesIO(f.read())

    except subprocess.CalledProcessError:
        return {'error': 'Processing failed'}, 500

    finally:
        os.remove(input_path)
        shutil.rmtree(output_dir)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=f"{file.filename}.{ext}",
        mimetype='application/octet-stream'
    )

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_file(f'static/{path}')

if __name__ == '__main__':
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel accessible at : {public_url}")

    # Replace the fetch URL in the JavaScript file
    js_path = 'static/script.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    pattern = r"fetch\(['\"](.*?/)?convert['\"]"
    replacement = f"fetch('{public_url}/convert'"
    new_js_content = re.sub(pattern, replacement, js_content)

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_js_content)

    app.run(port=5000)
