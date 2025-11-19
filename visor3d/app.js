/* ============================================
   LÓGICA VISOR 3D - MONITOREO IoT
   ============================================ */

// Configuración
const API_URL = 'https://q4gue6nm69.execute-api.us-east-1.amazonaws.com/default/getDatosSensores';
const SENSOR_POSITION = [-3.65, 1.07, -5.61];
const CAMERA_POSITION = [-2.5, 2.0, -4.5];

// ============================================
// CONFIGURACIÓN DE ACTUALIZACIÓN AUTOMÁTICA
// ============================================
const INTERVALO_ACTUALIZACION = 30000; // 30 segundos (configurable)
let intervaloActualizacion = null;
let ultimosDatos = null;

// ============================================
// CONTROL DEL SIDEBAR
// ============================================

function crearBotonSidebar() {
	const button = document.createElement('button');
	button.className = 'sidebar-toggle';
	button.innerHTML = `
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
			<path d="M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2z"/>
		</svg>
	`;
	
	button.addEventListener('click', toggleSidebar);
	document.body.appendChild(button);
	
	return button;
}

function toggleSidebar() {
	const sidebar = document.getElementById('potree_sidebar_container');
	const button = document.querySelector('.sidebar-toggle');
	
	if (sidebar && button) {
		sidebar.classList.toggle('visible');
		button.classList.toggle('sidebar-visible');
	}
}

// ============================================
// CONTROL DEL PANEL LATERAL
// ============================================

function abrirPanel() {
	const panel = document.getElementById('sensor-panel');
	const overlay = document.getElementById('panel-overlay');
	
	panel.classList.add('open');
	overlay.classList.add('visible');
	
	// Cargar datos actualizados
	cargarDatosPanel();
}

function cerrarPanel() {
	const panel = document.getElementById('sensor-panel');
	const overlay = document.getElementById('panel-overlay');
	
	panel.classList.remove('open');
	overlay.classList.remove('visible');
}

// Event listeners para el panel
document.addEventListener('DOMContentLoaded', () => {
	const closeBtn = document.getElementById('close-panel');
	const overlay = document.getElementById('panel-overlay');
	
	if (closeBtn) {
		closeBtn.addEventListener('click', cerrarPanel);
	}
	
	if (overlay) {
		overlay.addEventListener('click', cerrarPanel);
	}
});

// ============================================
// FUNCIONES DE DATOS
// ============================================

async function getSensorData() {
	try {
		console.log('🔄 Obteniendo datos de sensores...');
		const response = await fetch(API_URL);
		const data = await response.json();
		
		if (data.ultimo_dato) {
			const ts = typeof data.ultimo_dato.timestamp === 'string' 
				? parseInt(data.ultimo_dato.timestamp) 
				: data.ultimo_dato.timestamp;
			
			const resultado = {
				temperatura: data.ultimo_dato.temperatura || 0,
				humedad: data.ultimo_dato.humedad || 0,
				co2: data.ultimo_dato.ppm || 0,
				fecha: new Date(ts)
			};
			
			console.log('✅ Datos obtenidos:', resultado);
			return resultado;
		}
		
		console.warn('⚠️ No se encontró ultimo_dato');
		return null;
	} catch (error) {
		console.error('❌ Error:', error);
		return null;
	}
}

// ============================================
// FUNCIONES DE FORMATO
// ============================================

function formatearFecha(fecha) {
	return fecha.toLocaleString('es-ES', {
		day: '2-digit',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit'
	});
}

function getTemperatureStatus(temp) {
	if (temp < 18) return { text: "Frío", color: "#3b82f6", class: "frio" };
	if (temp > 26) return { text: "Caliente", color: "#ef4444", class: "caliente" };
	return { text: "Óptimo", color: "#10b981", class: "optimo" };
}

function getHumidityStatus(hum) {
	if (hum < 30) return { text: "Seco", color: "#f59e0b", class: "seco" };
	if (hum > 60) return { text: "Húmedo", color: "#3b82f6", class: "humedo" };
	return { text: "Óptimo", color: "#10b981", class: "optimo" };
}

function getCO2Status(co2) {
	if (co2 < 600) return { text: "Excelente", color: "#10b981", class: "excelente" };
	if (co2 < 1000) return { text: "Bueno", color: "#f59e0b", class: "bueno" };
	return { text: "Atención", color: "#ef4444", class: "atencion" };
}

// ============================================
// ETIQUETA FLOTANTE SIMPLE
// ============================================

function crearEtiquetaFlotante(data) {
	const label = document.createElement('div');
	label.className = 'sensor-label-floating';
	label.id = 'sensor-floating-label';
	
	if (data) {
		label.innerHTML = `
			<div><span class="value">${data.temperatura.toFixed(1)}°C</span> | 
			<span class="value">${data.humedad.toFixed(1)}%</span> | 
			<span class="value">${Math.round(data.co2)} ppm</span></div>
		`;
	} else {
		label.innerHTML = `<div>Cargando...</div>`;
	}
	
	document.body.appendChild(label);
	return label;
}

function actualizarPosicionEtiqueta() {
	const label = document.getElementById('sensor-floating-label');
	if (!label || !window.viewer) return;
	
	const annotation = window.viewer.scene.annotations.children[0];
	if (!annotation) return;
	
	const position = annotation.position;
	const camera = window.viewer.scene.getActiveCamera();
	const domElement = window.viewer.renderer.domElement;
	
	const vector = position.clone();
	vector.project(camera);
	
	const x = (vector.x + 1) / 2 * domElement.clientWidth;
	const y = -(vector.y - 1) / 2 * domElement.clientHeight;
	
	// Posicionar etiqueta DEBAJO del marcador
	const labelWidth = label.offsetWidth;
	label.style.left = (x - labelWidth / 2) + 'px';
	label.style.top = (y + 35) + 'px';
}

// ============================================
// ACTUALIZAR ETIQUETA FLOTANTE CON NUEVOS DATOS
// ============================================

function actualizarEtiquetaFlotante(data) {
	const label = document.getElementById('sensor-floating-label');
	if (!label || !data) return;
	
	// Agregar clase de animación
	label.classList.add('updating');
	
	// Actualizar contenido
	label.innerHTML = `
		<div><span class="value">${data.temperatura.toFixed(1)}°C</span> | 
		<span class="value">${data.humedad.toFixed(1)}%</span> | 
		<span class="value">${Math.round(data.co2)} ppm</span></div>
	`;
	
	// Remover clase de animación después de completarse
	setTimeout(() => {
		label.classList.remove('updating');
	}, 500);
	
	console.log('🏷️ Etiqueta flotante actualizada');
}

// ============================================
// CARGAR DATOS EN EL PANEL
// ============================================

async function cargarDatosPanel() {
	const container = document.getElementById('panel-data');
	
	// Usar datos en caché si están disponibles, sino obtener nuevos
	const data = ultimosDatos || await getSensorData();
	
	if (data) {
		const tempStatus = getTemperatureStatus(data.temperatura);
		const humStatus = getHumidityStatus(data.humedad);
		const co2Status = getCO2Status(data.co2);
		
		container.innerHTML = `
			<div class="sensor-data-grid">
				<div class="sensor-card-panel">
					<div class="label">🌡️ Temperatura</div>
					<div class="value-container">
						<span class="value" style="color: ${tempStatus.color}">${data.temperatura.toFixed(1)}</span>
						<span class="unit">°C</span>
					</div>
					<div class="status ${tempStatus.class}">${tempStatus.text}</div>
				</div>
				
				<div class="sensor-card-panel">
					<div class="label">💧 Humedad</div>
					<div class="value-container">
						<span class="value" style="color: ${humStatus.color}">${data.humedad.toFixed(1)}</span>
						<span class="unit">%</span>
					</div>
					<div class="status ${humStatus.class}">${humStatus.text}</div>
				</div>
				
				<div class="sensor-card-panel">
					<div class="label">🌬️ Calidad del Aire (CO₂)</div>
					<div class="value-container">
						<span class="value" style="color: ${co2Status.color}">${Math.round(data.co2)}</span>
						<span class="unit">ppm</span>
					</div>
					<div class="status ${co2Status.class}">${co2Status.text}</div>
				</div>
			</div>
			
			<div class="last-update-panel">
				🕐 Última actualización: ${formatearFecha(data.fecha)}
			</div>
		`;
	} else {
		container.innerHTML = `
			<div style="text-align: center; padding: 40px; color: #ef4444;">
				⚠️ Error al cargar datos
			</div>
		`;
	}
}

// ============================================
// ACTUALIZAR PANEL LATERAL SI ESTÁ ABIERTO
// ============================================

function actualizarPanelSiAbierto(data) {
	const panel = document.getElementById('sensor-panel');
	
	// Verificar si el panel está abierto
	if (panel && panel.classList.contains('open')) {
		const container = document.getElementById('panel-data');
		
		if (data && container) {
			const tempStatus = getTemperatureStatus(data.temperatura);
			const humStatus = getHumidityStatus(data.humedad);
			const co2Status = getCO2Status(data.co2);
			
			// Agregar animación sutil
			container.style.opacity = '0.7';
			
			setTimeout(() => {
				container.innerHTML = `
					<div class="sensor-data-grid">
						<div class="sensor-card-panel">
							<div class="label">🌡️ Temperatura</div>
							<div class="value-container">
								<span class="value" style="color: ${tempStatus.color}">${data.temperatura.toFixed(1)}</span>
								<span class="unit">°C</span>
							</div>
							<div class="status ${tempStatus.class}">${tempStatus.text}</div>
						</div>
						
						<div class="sensor-card-panel">
							<div class="label">💧 Humedad</div>
							<div class="value-container">
								<span class="value" style="color: ${humStatus.color}">${data.humedad.toFixed(1)}</span>
								<span class="unit">%</span>
							</div>
							<div class="status ${humStatus.class}">${humStatus.text}</div>
						</div>
						
						<div class="sensor-card-panel">
							<div class="label">🌬️ Calidad del Aire (CO₂)</div>
							<div class="value-container">
								<span class="value" style="color: ${co2Status.color}">${Math.round(data.co2)}</span>
								<span class="unit">ppm</span>
							</div>
							<div class="status ${co2Status.class}">${co2Status.text}</div>
						</div>
					</div>
					
					<div class="last-update-panel">
						🕐 Última actualización: ${formatearFecha(data.fecha)}
					</div>
				`;
				
				// Restaurar opacidad con transición suave
				container.style.opacity = '1';
				
				console.log('📊 Panel lateral actualizado');
			}, 150);
		}
	}
}

// ============================================
// SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA
// ============================================

async function actualizarDatosSensores() {
	console.log('🔄 Actualizando datos automáticamente...');
	
	const nuevosDatos = await getSensorData();
	
	if (nuevosDatos) {
		// Guardar en caché
		ultimosDatos = nuevosDatos;
		
		// Actualizar etiqueta flotante
		actualizarEtiquetaFlotante(nuevosDatos);
		
		// Actualizar panel si está abierto
		actualizarPanelSiAbierto(nuevosDatos);
		
		console.log('✅ Actualización completada');
	} else {
		console.warn('⚠️ No se pudieron obtener nuevos datos');
	}
}

function iniciarActualizacionAutomatica() {
	// Limpiar intervalo anterior si existe
	if (intervaloActualizacion) {
		clearInterval(intervaloActualizacion);
	}
	
	// Configurar nuevo intervalo
	intervaloActualizacion = setInterval(actualizarDatosSensores, INTERVALO_ACTUALIZACION);
	
	console.log(`⏰ Actualización automática iniciada (cada ${INTERVALO_ACTUALIZACION / 1000} segundos)`);
}

function detenerActualizacionAutomatica() {
	if (intervaloActualizacion) {
		clearInterval(intervaloActualizacion);
		intervaloActualizacion = null;
		console.log('⏸️ Actualización automática detenida');
	}
}

// ============================================
// HACER RESPONSIVE EL VIEWER
// ============================================

function hacerResponsive() {
	if (window.viewer) {
		const resize = () => {
			if (window.viewer.renderer) {
				const width = window.innerWidth;
				const height = window.innerHeight;
				window.viewer.renderer.setSize(width, height);
				
				if (window.viewer.scene && window.viewer.scene.camera) {
					window.viewer.scene.camera.aspect = width / height;
					window.viewer.scene.camera.updateProjectionMatrix();
				}
				
				actualizarPosicionEtiqueta();
			}
		};
		
		window.addEventListener('resize', resize);
		resize();
	}
}

// ============================================
// INICIALIZACIÓN DE POTREE
// ============================================

async function inicializarVisor() {
	console.log('🚀 Inicializando visor 3D...');
	
	// Crear botón del sidebar
	crearBotonSidebar();
	
	// Configurar viewer
	window.viewer = new Potree.Viewer(document.getElementById("potree_render_area"));
	viewer.setEDLEnabled(true);
	viewer.setFOV(60);
	viewer.setPointBudget(1_500_000);
	viewer.loadSettingsFromURL();
	viewer.setBackground("gradient");
	viewer.setDescription("Monitoreo Ambiental IoT");
	
	// Hacer responsive
	hacerResponsive();
	
	// Cargar GUI
	viewer.loadGUI(() => {
		viewer.setLanguage('es');
		$("#menu_tools").next().show();
		$("#menu_clipping").next().show();
	});
	
	// Cargar modelo 3D
	Potree.loadPointCloud("../pointclouds/mi_espacio_3d/metadata.json", "Mi Espacio 3D", async e => {
		let scene = viewer.scene;
		let pointcloud = e.pointcloud;
		let material = pointcloud.material;
		
		material.size = 1.2;
		material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
		material.shape = Potree.PointShape.CIRCLE;
		
		scene.addPointCloud(pointcloud);
		viewer.fitToScreen();
		
		// Obtener datos de sensores
		console.log('📊 Cargando datos de sensores...');
		const sensorData = await getSensorData();
		
		// Guardar datos iniciales
		ultimosDatos = sensorData;
		
		// Crear etiqueta flotante
		crearEtiquetaFlotante(sensorData);
		
		// Crear anotación de Potree (comportamiento por defecto)
		let annotation = new Potree.Annotation({
			position: SENSOR_POSITION,
			title: "🌡️ Estación de Sensores IoT",
			cameraPosition: CAMERA_POSITION,
			cameraTarget: SENSOR_POSITION,
			description: ''
		});
		
		// Al hacer clic, abrir panel (dejando que Potree haga su animación)
		annotation.addEventListener("click", () => {
			abrirPanel();
		});
		
		viewer.scene.annotations.add(annotation);
		
		// Actualizar posición de etiqueta en cada frame
		viewer.addEventListener("update", actualizarPosicionEtiqueta);
		
		// ⭐ INICIAR ACTUALIZACIÓN AUTOMÁTICA
		iniciarActualizacionAutomatica();
		
		console.log('✅ Visor inicializado correctamente');
	});
}

// Detener actualización cuando se cierre/oculte la página
document.addEventListener('visibilitychange', () => {
	if (document.hidden) {
		detenerActualizacionAutomatica();
		console.log('👁️ Página oculta - actualización pausada');
	} else {
		iniciarActualizacionAutomatica();
		// Actualizar inmediatamente al volver a la página
		actualizarDatosSensores();
		console.log('👁️ Página visible - actualización reanudada');
	}
});

// Iniciar cuando el DOM esté listo
if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', inicializarVisor);
} else {
	inicializarVisor();
}