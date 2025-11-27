from flask import Flask, render_template, send_from_directory, Response, jsonify, request
import os
import cv2
import numpy as np
import time

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.template_folder = os.path.join(BASE_DIR, 'templates')
app.static_folder = os.path.join(BASE_DIR, 'static')

print("🔍 DIAGNÓSTICO COMPLETO:")
print("📁 Templates:", os.listdir(app.template_folder))
print("📁 Static/css:", os.listdir(os.path.join(app.static_folder, 'css')))
print("📁 Static/js:", os.listdir(os.path.join(app.static_folder, 'js')))

# Simular función de video para la demo
def generar_frames_demo():
    """Genera frames de demostración para el streaming de video"""
    while True:
        # Crear imagen de demostración
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "Sistema de Asistencia Facial", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Modo Demostracion - Flask", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.rectangle(frame, (200, 150), (440, 390), (0, 255, 0), 2)
        cv2.putText(frame, "Reconocimiento Activo", (180, 140), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Codificar frame como JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.1)

# RUTAS PRINCIPALES
@app.route('/')
def home():
    return '''
    <h1>Opciones de prueba:</h1>
    <ul>
        <li><a href="/template">Template Original (app principal)</a></li>
        <li><a href="/fixed">Template Fixed</a></li>
        <li><a href="/simple">Template Simple</a></li>
    </ul>
    '''

@app.route('/template')
def template():
    print("📄 Cargando template ORIGINAL...")
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>Error: {e}</h1>"

@app.route('/fixed')
def fixed():
    print("📄 Cargando template FIXED...")
    try:
        return render_template('index_fixed.html')
    except Exception as e:
        return f"<h1>Error: {e}</h1>"

@app.route('/simple')
def simple():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Simple</title></head>
    <body>
        <h1>Template Simple</h1>
        <p>Sin CSS/JS externos</p>
        <button onclick="alert('JS funciona')">Probar JS</button>
    </body>
    </html>
    '''

# RUTAS DE LA APLICACIÓN PRINCIPAL (para que funcionen los templates)
@app.route('/video_feed')
def video_feed():
    """Streaming de video"""
    return Response(generar_frames_demo(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/iniciar_reconocimiento', methods=['POST'])
def iniciar_reconocimiento():
    return jsonify({
        'status': 'success',
        'message': 'Sistema de reconocimiento iniciado',
        'asistencia': 'Gus - 26/11/2025 19:40:00'
    })

@app.route('/detener_reconocimiento', methods=['POST'])
def detener_reconocimiento():
    return jsonify({
        'status': 'success', 
        'message': 'Sistema de reconocimiento detenido'
    })

@app.route('/obtener_asistencias')
def obtener_asistencias():
    return jsonify({
        'asistencias': [
            {'Nombre': 'Gus', 'Fecha': '26/11/2025', 'Hora': '19:40:00'},
            {'Nombre': 'Usuario Demo', 'Fecha': '26/11/2025', 'Hora': '19:41:00'}
        ]
    })

@app.route('/estado_sistema')
def estado_sistema():
    return jsonify({
        'estado_camara': 'activa',
        'personas_registradas': 9,
        'ultima_asistencia': 'Gus - 26/11/2025 19:40:00',
        'total_asistencias_hoy': 2
    })

# Ruta para archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)