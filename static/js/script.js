// VERSIÓN CORREGIDA - SIN ERRORES DE SINTAXIS
console.log('✅ script.js cargado - VERSIÓN CORREGIDA');

// Función para INICIAR reconocimiento
function iniciarReconocimiento() {
    console.log('🎬 Botón INICIAR presionado');
    fetch('/iniciar_reconocimiento', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Respuesta:', data);
            alert('✅ ' + data.message);
            if (typeof actualizarEstado === 'function') {
                actualizarEstado();
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            alert('❌ Error al iniciar reconocimiento');
        });
}

// Función para DETENER reconocimiento
function detenerReconocimiento() {
    console.log('⏹️ Botón DETENER presionado');
    fetch('/detener_reconocimiento', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Respuesta:', data);
            alert('🛑 ' + data.message);
            if (typeof actualizarEstado === 'function') {
                actualizarEstado();
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            alert('❌ Error al detener reconocimiento');
        });
}

// Función para VER ASISTENCIAS
function verAsistencias() {
    console.log('📊 Botón VER ASISTENCIAS presionado');
    const resultados = document.getElementById('resultados');
    const lista = document.getElementById('lista-asistencias');
    
    if (!resultados || !lista) {
        console.error('❌ No se encontraron elementos del DOM');
        alert('Error: No se puede cargar el panel de asistencias');
        return;
    }
    
    fetch('/obtener_asistencias')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Asistencias recibidas:', data);
            if (data.asistencias && data.asistencias.length > 0) {
                lista.innerHTML = data.asistencias.map(function(asistencia) {
                    return '<div class="asistencia-item">' +
                           '<div><strong>' + asistencia.Nombre + '</strong>' +
                           '<div class="fecha-hora">' + asistencia.Fecha + ' • ' + asistencia.Hora + '</div>' +
                           '</div>' +
                           '<span class="badge">✅ Registrado</span>' +
                           '</div>';
                }).join('');
            } else {
                lista.innerHTML = '<div class="no-asistencias">No hay asistencias registradas aún</div>';
            }
            
            resultados.style.display = 'block';
        })
        .catch(error => {
            console.error('❌ Error:', error);
            lista.innerHTML = '<div class="error">Error al cargar asistencias</div>';
            resultados.style.display = 'block';
        });
}

// Función para actualizar estado
function actualizarEstado() {
    fetch('/estado_sistema')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Estado actualizado:', data);
            const estadoCamara = document.getElementById('estado-camara');
            const personasRegistradas = document.getElementById('personas-registradas');
            const ultimaAsistencia = document.getElementById('ultima-asistencia');
            
            if (estadoCamara) estadoCamara.textContent = data.estado_camara || '---';
            if (personasRegistradas) personasRegistradas.textContent = data.personas_registradas || '---';
            if (ultimaAsistencia) ultimaAsistencia.textContent = data.ultima_asistencia || '---';
        })
        .catch(error => console.error('❌ Error actualizando estado:', error));
}

// Hacer funciones globales
window.iniciarReconocimiento = iniciarReconocimiento;
window.detenerReconocimiento = detenerReconocimiento;
window.verAsistencias = verAsistencias;
window.actualizarEstado = actualizarEstado;

console.log('✅ Todas las funciones definidas correctamente');
