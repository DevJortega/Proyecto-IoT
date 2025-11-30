# 🌐 Sistema IoT con Conectividad LTE y Visualización en la Nube

Sistema IoT completo para monitoreo ambiental con ESP32, conectividad LTE/4G, AWS IoT Core, dashboard interactivo en React y visualización 3D con Potree.

**🌐 Sitio Web:**
- 📊 **Dashboard**: https://iot-proyecto.duckdns.org/dashboard/
- 🎯 **Visor 3D**: https://iot-proyecto.duckdns.org/visor3d/

---

## 📁 Estructura del Proyecto

### 📡 [Esp32/](./Esp32/)
Código MicroPython para el ESP32 con sensores ambientales, conectado a AWS IoT Core vía LTE.

**Hardware:**
- LilyGo T-A7670 R2 (ESP32 + Módem LTE)
- Sensor DHT22 (Temperatura y Humedad)
- Sensor MQ135 (Calidad del Aire / CO₂)
- Display OLED 0.96" (I2C)

**Características:**
- ✅ Conexión a AWS IoT Core vía MQTT/TLS 1.2
- ✅ Publicación de datos cada 60 segundos
- ✅ Autenticación con certificados X.509
- ✅ Tiempo de conexión: ~4-5 minutos
- ✅ Feedback visual en display OLED

[📖 Ver código ESP32 →](./Esp32/)

---

### 📊 [dashboard/](./dashboard/)
Dashboard web interactivo desarrollado en **React** para visualización en tiempo real.

**🌐 Ver en vivo:** https://iot-proyecto.duckdns.org/dashboard/

**Características:**
- ✅ Visualización en tiempo real de temperatura, humedad y CO₂
- ✅ Gráficos históricos con Recharts
- ✅ Periodo seleccionable (última semana)
- ✅ Modal expandible para análisis detallado
- ✅ Diseño responsive (desktop/móvil)
- ✅ Actualización inteligente (solo cuando hay datos nuevos)
- ✅ Indicadores de calidad del aire codificados por color

**Stack Tecnológico:**
- React 18
- Recharts (gráficos)
- Lucide React (iconos)
- Tailwind CSS (estilos)
- AWS Lambda + API Gateway (backend)

**Arquitectura:**
```
Dashboard React → API Gateway → Lambda → DynamoDB
```

---

### 🎯 [visor3d/](./visor3d/)
Visor tridimensional con **Potree** que integra nube de puntos del salón con datos de sensores.

**🌐 Ver en vivo:** https://iot-proyecto.duckdns.org/visor3d/

**Características:**
- ✅ Nube de puntos 3D del salón escaneado
- ✅ Marcador de ubicación del sensor
- ✅ Panel lateral con datos en tiempo real
- ✅ Actualización automática cada 30 segundos
- ✅ Navegación interactiva (rotación, zoom, pan)
- ✅ Etiquetas flotantes con información instantánea

**Stack Tecnológico:**
- Potree (visualización 3D)
- Three.js (motor 3D)
- WebGL
- JavaScript vanilla

---

## 🚀 Arquitectura del Sistema
```
┌─────────────────┐       ┌──────────────┐       ┌─────────────┐
│  ESP32 + LTE    │──4G──▶│ AWS IoT Core │──────▶│  DynamoDB   │
│  DHT22 + MQ135  │       │   (MQTT/TLS) │       │             │
└─────────────────┘       └──────────────┘       └─────────────┘
                                                          │
                                                          │
┌─────────────────┐       ┌──────────────┐       ┌──────▼──────┐
│  Usuario Web    │◀─────▶│   Nginx EC2  │◀─────▶│   Lambda +  │
│ (Dashboard/3D)  │       │     HTTPS    │       │ API Gateway │
└─────────────────┘       └──────────────┘       └─────────────┘
```

---

## 📊 Flujo de Datos

1. **Captura**: ESP32 lee sensores DHT22 y MQ135
2. **Transmisión**: Envío vía LTE/4G a AWS IoT Core (MQTT/TLS)
3. **Almacenamiento**: Regla IoT Core → DynamoDB con timestamp
4. **API**: Lambda consulta DynamoDB cuando es invocada
5. **Visualización**: Dashboard/Potree consultan API periódicamente
6. **Usuario**: Visualiza datos en tiempo real en navegador

---

## 📋 Formato de Datos

### Mensaje MQTT (desde ESP32)
```json
{
  "device_id": "ESP32_SENSORES_38182bf824ac",
  "contador": 42,
  "temperatura": 31.3,
  "humedad": 80.4,
  "ppm": 277
}
```

### Respuesta API (con timestamp de AWS)
```json
{
  "device_id": "ESP32_SENSORES_38182bf824ac",
  "timestamp": "1760762625251",
  "temperatura": 31.3,
  "humedad": 80.4,
  "ppm": 277,
  "contador": 42
}
```

---

## 🛠️ Tecnologías Utilizadas

### Hardware
- **Microcontrolador**: ESP32 (LilyGo T-A7670 R2)
- **Conectividad**: Módem LTE A7670 (Cat-1)
- **Sensores**: DHT22, MQ135
- **Display**: OLED 0.96" I2C

### Backend & Cloud
- **Cloud Platform**: AWS IoT Core
- **Base de Datos**: Amazon DynamoDB
- **Serverless**: AWS Lambda (Python)
- **API**: AWS API Gateway (REST)
- **Protocolo**: MQTT over TLS 1.2
- **Autenticación**: Certificados X.509

### Frontend
- **Dashboard**: React 18 + Recharts + Tailwind CSS
- **Visor 3D**: Potree + Three.js + WebGL
- **Servidor**: Nginx en EC2 (Ubuntu 24.04)
- **SSL**: Let's Encrypt + DuckDNS

### Desarrollo
- **Firmware**: MicroPython
- **Control de versiones**: Git + GitHub
- **Despliegue**: SCP + SSH

---

## 💰 Costos de Operación

### Configuración actual:
- **Frecuencia**: 1 mensaje cada 60 segundos
- **Dispositivos**: 1
- **Operación**: 24/7

### Costos mensuales estimados:
| Servicio | Costo |
|----------|-------|
| AWS IoT Core | $0.055 |
| DynamoDB | $0.083 |
| Lambda + API Gateway | ~$0.050 |
| EC2 t2.micro (750h gratis) | $0.000 |
| **TOTAL** | **~$0.19 USD/mes** |

---

## 🎯 Estado del Proyecto

### ✅ Completado
- [x] Código ESP32 con MicroPython
- [x] Conexión LTE/4G a AWS IoT Core
- [x] Lectura de sensores DHT22 y MQ135
- [x] Publicación MQTT con SSL/TLS
- [x] Display OLED con información de estado
- [x] Almacenamiento en DynamoDB
- [x] API REST con Lambda + API Gateway
- [x] Dashboard React con gráficos en tiempo real
- [x] Visor 3D Potree con nube de puntos
- [x] Despliegue en EC2 con Nginx + SSL
- [x] Dominio con DuckDNS

### 🚧 Próximas Mejoras
- [ ] Alertas por correo (SNS)
- [ ] Múltiples dispositivos
- [ ] Análisis predictivo
- [ ] App móvil

---

## 🚀 Inicio Rápido

### 1. Clonar repositorio
```bash
git clone https://github.com/DevJortega/Proyecto-IoT.git
cd Proyecto-IoT
```

### 2. Configurar ESP32
```bash
cd Esp32
# Copiar certificados de AWS IoT Core
# Configurar credenciales en main.py
# Flashear a ESP32
```

### 3. Ver Dashboard
Abre en navegador: https://iot-proyecto.duckdns.org/dashboard/

### 4. Ver Visor 3D
Abre en navegador: https://iot-proyecto.duckdns.org/visor3d/

---

## 🔧 Instalación Local (Dashboard)
```bash
# Instalar dependencias
cd dashboard-src
npm install

# Ejecutar en desarrollo
npm start

# Compilar para producción
npm run build
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si quieres colaborar:

1. **Fork** el proyecto
2. Crea una **rama** (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** (`git commit -m 'Agrega nueva funcionalidad'`)
4. **Push** (`git push origin feature/nueva-funcionalidad`)
5. Abre un **Pull Request**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENCE.md](LICENCE.md) para más detalles.

---

## 🔒 Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas certificados `.pem` o `.key` al repositorio
- Nunca subas credenciales de AWS
- Usa `.gitignore` para proteger información sensible
- Rota certificados si fueron expuestos

---

## 🙏 Agradecimientos

- [LilyGo](https://www.lilygo.cc/) - Hardware T-A7670
- [AWS IoT Core](https://aws.amazon.com/iot-core/) - Plataforma cloud
- [MicroPython](https://micropython.org/) - Firmware ESP32
- [Potree](https://github.com/potree/potree) - Visualización 3D
- [React](https://react.dev/) - Framework frontend
- Universidad del Norte - Asignatura Comunicaciones

---

## 👥 Autores

**Proyecto de Comunicaciones - Universidad del Norte**

- María José Romero
- Jorge Ortega Anillo
- Juan Diego Acevedo
- Juan Felipe Padrón

**Docente:** Juan Carlos Vélez Díaz

---

<p align="center">
  <b>🌐 Sistema IoT con LTE + AWS + Visualización 3D</b><br>
  <sub>Monitoreo ambiental en tiempo real | Universidad del Norte 2025</sub>
</p>
