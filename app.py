import os
import cv2
import numpy as np
import face_recognition
from flask import Flask, render_template, request, jsonify, Response
import requests
from io import BytesIO
from PIL import Image
import rarfile
import csv
from datetime import datetime
import time

app = Flask(__name__)

# Variables globales para el reconocimiento facial
lista_codificaciones = []
lista_nombres = []
caras_registradas = set()
ultima_asistencia = ""
estado_camara = "detenida"

def inicializar_sistema():
    """Inicializa el sistema de reconocimiento facial"""
    global lista_codificaciones, lista_nombres
    
    try:
        # Configurar herramienta UnRAR
        rarfile.UNRAR_TOOL = r"E:\unrar\UnRAR.exe"
        
        # URL del RAR en Google Drive (tu dataset en la nube)
        url_rar = "https://drive.google.com/uc?export=download&id=1HDUQre_8ujk_6TNtNvPvrIeBVHUJ5vHj"
        
        print("⬇ Descargando fotos desde Drive...")
        response = requests.get(url_rar)
        if response.status_code != 200:
            raise Exception("No se pudo descargar el archivo RAR desde Drive")

        # Guardar RAR temporalmente
        ruta_rar_temp = "temp_fotos.rar"
        with open(ruta_rar_temp, "wb") as f:
            f.write(response.content)

        # Extraer imágenes del RAR
        print("⬇ Extrayendo imágenes del RAR...")
        with rarfile.RarFile(ruta_rar_temp) as rf:
            lista_codificaciones = []
            lista_nombres = []
            for archivo in rf.namelist():
                if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                    with rf.open(archivo) as img_file:
                        img = Image.open(img_file).convert("RGB")
                        img_np = np.array(img)
                        cods = face_recognition.face_encodings(img_np)
                        if len(cods) > 0:
                            lista_codificaciones.append(cods[0])
                            lista_nombres.append("Gus")  # Todos los archivos son de Gustavo
                        else:
                            print(f"⚠ No se detectó cara en la imagen {archivo}")
        
        # Limpiar archivo temporal
        if os.path.exists(ruta_rar_temp):
            os.remove(ruta_rar_temp)
            
        print(f"✅ Total de codificaciones cargadas: {len(lista_codificaciones)}")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar el sistema: {str(e)}")
        return False

def registrar_asistencia(nombre):
    """Registra la asistencia en el archivo CSV"""
    global caras_registradas, ultima_asistencia
    
    if nombre != "Desconocido" and nombre not in caras_registradas:
        archivo_asistencia = "asistencia_version3.csv"
        
        # Crear archivo si no existe
        if not os.path.exists(archivo_asistencia):
            with open(archivo_asistencia, "w", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Nombre", "Fecha", "Hora"])
        
        # Registrar asistencia
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        hora = ahora.strftime("%H:%M:%S")
        
        with open(archivo_asistencia, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([nombre, fecha, hora])
        
        caras_registradas.add(nombre)
        ultima_asistencia = f"{nombre} - {fecha} {hora}"
        print(f"✅ Asistencia registrada: {ultima_asistencia}")
        return True
    
    return False

def generar_frames():
    """Genera frames para el streaming de video - MODO REAL con reconocimiento facial"""
    global estado_camara, lista_codificaciones, lista_nombres
    
    try:
        # Desarrollo local - usar cámara real
        camara = cv2.VideoCapture(0)
        camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    except:
        # Fallback: imagen estática si no hay cámara
        camara = None
        img_estatica = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img_estatica, "Error al acceder a la camara", 
                   (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    estado_camara = "activa"
    
    while estado_camara == "activa":
        try:
            if camara and camara.isOpened():
                ret, frame = camara.read()
                if not ret:
                    break
                    
                # 🔍 RECONOCIMIENTO FACIAL EN TIEMPO REAL (como tu versión original)
                # Reducir tamaño para acelerar procesamiento
                frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                frame_pequeno_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)
                
                # Detectar caras en el frame actual
                ubicaciones_caras = face_recognition.face_locations(frame_pequeno_rgb)
                codificaciones_caras = face_recognition.face_encodings(frame_pequeno_rgb, ubicaciones_caras)
                
                for cod_cara, ubic_cara in zip(codificaciones_caras, ubicaciones_caras):
                    # Comparar con caras conocidas
                    coincidencias = face_recognition.compare_faces(lista_codificaciones, cod_cara)
                    nombre = "Desconocido"
                    
                    # Calcular distancias y encontrar mejor coincidencia
                    distancias = face_recognition.face_distance(lista_codificaciones, cod_cara)
                    if len(distancias) > 0:
                        indice_mejor = np.argmin(distancias)
                        if coincidencias[indice_mejor]:
                            nombre = lista_nombres[indice_mejor]
                            
                            # Registrar asistencia automáticamente
                            if estado_camara == "activa":
                                registrar_asistencia(nombre)
                    
                    # Escalar coordenadas de vuelta al tamaño original
                    top, right, bottom, left = ubic_cara
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Dibujar recuadro y nombre
                    color = (0, 255, 0) if nombre != "Desconocido" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, nombre, (left + 6, bottom - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            else:
                # Modo demostración sin cámara
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Sistema de Asistencia Facial", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Modo: Reconocimiento Activo", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Personas registradas: {len(lista_codificaciones)}", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Codificar frame como JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # Controlar FPS
            
        except Exception as e:
            print(f"Error en generacion de frames: {e}")
            break
    
    if camara:
        camara.release()
    estado_camara = "detenida"

# ================= RUTAS FLASK =================

@app.route('/')
def index():
    """Página principal - Interfaz web"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Streaming de video con reconocimiento facial en tiempo real"""
    return Response(generar_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/iniciar_reconocimiento', methods=['POST'])
def iniciar_reconocimiento():
    """Inicia el sistema de reconocimiento facial"""
    global estado_camara
    estado_camara = "activa"
    return jsonify({
        'status': 'success',
        'message': 'Sistema de reconocimiento facial iniciado',
        'personas_registradas': len(lista_codificaciones)
    })

@app.route('/detener_reconocimiento', methods=['POST'])
def detener_reconocimiento():
    """Detiene el sistema de reconocimiento facial"""
    global estado_camara
    estado_camara = "detenida"
    return jsonify({
        'status': 'success', 
        'message': 'Sistema de reconocimiento detenido'
    })

@app.route('/obtener_asistencias')
def obtener_asistencias():
    """Obtiene el historial de asistencias"""
    try:
        asistencias = []
        if os.path.exists("asistencia_version3.csv"):
            with open("asistencia_version3.csv", "r", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                asistencias = list(reader)
        return jsonify({'asistencias': asistencias})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/estado_sistema')
def estado_sistema():
    """Retorna el estado actual del sistema"""
    return jsonify({
        'estado_camara': estado_camara,
        'personas_registradas': len(lista_codificaciones),
        'ultima_asistencia': ultima_asistencia,
        'total_asistencias_hoy': len(caras_registradas)
    })

@app.route('/resultados')
def resultados():
    """Página de resultados de asistencias"""
    return render_template('resultados.html')

# ================= INICIALIZACIÓN =================

if __name__ == '__main__':
    # Inicializar el sistema de reconocimiento facial
    print("🚀 Inicializando sistema de reconocimiento facial...")
    print("📊 Cargando dataset desde la nube...")
    
    if inicializar_sistema():
        print("✅ Sistema inicializado correctamente")
        print(f"👤 Personas registradas: {len(lista_codificaciones)}")
    else:
        print("❌ Error en la inicialización del sistema")
    
    # Ejecutar servidor Flask
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Servidor Flask iniciado en puerto {port}")
    print(f"📱 Accede en: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)