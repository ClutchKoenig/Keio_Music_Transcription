import os, re, tempfile, shutil, subprocess, uuid, threading, time
from flask import Flask, request, send_file, Response, jsonify
from flask_cors import CORS
from io import BytesIO
from pyngrok import ngrok
from src.run_model import process_audio
from src.progress_tracker import progress_tracker

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

    # Generate unique session ID for progress tracking
    session_id = str(uuid.uuid4())
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
        file.save(tmp_input.name)
        input_path = tmp_input.name

    output_dir = tempfile.mkdtemp()

    def process_in_background():
        try:
            process_audio(input_path, output_dir, format, session_id)
        except Exception as e:
            progress_tracker.error_session(session_id, str(e))
        finally:
            # Cleanup will be handled by the progress endpoint
            pass

    # Start processing in background
    thread = threading.Thread(target=process_in_background)
    thread.start()

    return jsonify({
        'session_id': session_id,
        'status': 'processing_started'
    })

@app.route('/progress/<session_id>')
def get_progress(session_id):
    """Server-Sent Events endpoint for progress updates"""
    def generate():
        while True:
            progress_data = progress_tracker.get_progress(session_id)
            if progress_data is None:
                yield f"data: {{'error': 'Session not found'}}\n\n"
                break
            
            import json
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            if progress_data['status'] in ['completed', 'error']:
                break
                
            time.sleep(1)  # Update every second
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<session_id>')
def download_result(session_id):
    """Download the converted file"""
    progress_data = progress_tracker.get_progress(session_id)
    
    if not progress_data or progress_data['status'] != 'completed':
        return {'error': 'File not ready or session not found'}, 404
    
    # Get the format from the session (we'll need to store this)
    # For now, let's check both directories
    output_dir = progress_data.get('output_dir')
    if not output_dir:
        return {'error': 'Output directory not found'}, 404
    
    # Try MIDI first, then PDF
    for format_type, ext, subdir in [('midi', 'mid', 'midi'), ('pdf', 'pdf', 'score')]:
        search_dir = os.path.join(output_dir, subdir)
        if os.path.exists(search_dir):
            output_files = [f for f in os.listdir(search_dir) if f.endswith(f".{ext}")]
            if output_files:
                output_path = os.path.join(search_dir, output_files[0])
                
                with open(output_path, 'rb') as f:
                    file_data = BytesIO(f.read())
                
                # Cleanup
                progress_tracker.cleanup_session(session_id)
                shutil.rmtree(output_dir, ignore_errors=True)
                
                return send_file(
                    file_data,
                    as_attachment=True,
                    download_name=f"conversion.{ext}",
                    mimetype='application/octet-stream'
                )
    
    return {'error': 'No output file found'}, 500

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
