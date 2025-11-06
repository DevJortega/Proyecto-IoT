# 🌐 Proyecto IoT - Monitoreo Ambiental

Sistema IoT completo para monitoreo de temperatura, humedad y calidad del aire con visualización en tiempo real.

## 📁 Estructura del Proyecto

### 📡 [Esp32/](./Esp32/)
Código para el ESP32 con sensores DHT22 y MQ135, conectado a AWS IoT Core vía LTE.

**Hardware:**
- LilyGo T-A7670 R2 (ESP32 + Módem LTE)
- Sensor DHT22 (Temperatura y Humedad)
- Sensor MQ135 (Calidad del Aire)

**Características:**
- Conexión a AWS IoT Core vía MQTT/TLS
- Publicación de datos cada 28 segundos
- Tiempo de conexión: ~4-5 minutos

[📖 Ver documentación completa →](./Esp32/README.md)

---

### 🌐 visualizacion-nube/
*(Próximamente)*

Dashboard web para visualización en tiempo real de los datos del sensor.

**Tecnologías planeadas:**
- Frontend: HTML5, CSS3, JavaScript
- Visualización: Chart.js / D3.js
- Backend: AWS Lambda + API Gateway
- Base de datos: AWS DynamoDB / Timestream

---

## 🚀 Inicio Rápido

### 1. Configurar ESP32
```bash
cd Esp32
# Seguir instrucciones en Esp32/README.md
```

### 2. Configurar Visualización Web
```bash
cd visualizacion-nube
# Próximamente
```

---

## 📊 Flujo de Datos

```
┌─────────────┐        ┌──────────────┐        ┌─────────────────┐
│   ESP32     │  MQTT  │  AWS IoT     │  Store │   DynamoDB/     │
│  + Sensores │───────>│   Core       │───────>│   Timestream    │
└─────────────┘  TLS   └──────────────┘        └─────────────────┘
                                                         │
                                                         │ Query
                                                         v
                                               ┌─────────────────┐
                                               │   Dashboard     │
                                               │   Web           │
                                               └─────────────────┘
```

---

## 📋 Formato de Datos

Los datos se publican en formato JSON al tópico MQTT `sensores`:

```json
{
  "device_id": "ESP32_SENSORES_xxxxx",
  "contador": 1,
  "temperatura": 25.5,
  "humedad": 65.3,
  "ppm": 450.2
}
```

---

## 🛠️ Tecnologías Utilizadas

### Hardware
- **Microcontrolador**: ESP32 (LilyGo T-A7670 R2)
- **Conectividad**: Módem LTE A7670
- **Sensores**: DHT22 (temperatura/humedad), MQ135 (calidad del aire)

### Software & Cloud
- **Firmware**: MicroPython
- **Cloud Platform**: AWS IoT Core
- **Protocolo**: MQTT over TLS 1.2
- **Certificados**: X.509 para autenticación

### Futuro (Visualización)
- AWS Lambda (serverless functions)
- API Gateway (REST API)
- DynamoDB / Timestream (almacenamiento)
- JavaScript (Chart.js / D3.js para gráficos)

---

## 📝 Estado del Proyecto

- [x] Código ESP32 funcional
- [x] Conexión a AWS IoT Core
- [x] Lectura de sensores DHT22 y MQ135
- [x] Publicación MQTT con SSL/TLS
- [x] Manejo de errores y reconexión
- [ ] Dashboard web de visualización
- [ ] API REST para consulta de datos
- [ ] Base de datos histórica
- [ ] Sistema de alertas por umbrales
- [ ] App móvil (opcional)

---

## 🎯 Roadmap

### Fase 1: Hardware ✅ (Completado)
- ✅ Implementación ESP32
- ✅ Integración sensores
- ✅ Conexión AWS IoT Core

### Fase 2: Visualización 🚧 (En desarrollo)
- [ ] Dashboard web básico
- [ ] Gráficos en tiempo real
- [ ] Almacenamiento de datos históricos

### Fase 3: Mejoras 📋 (Planeado)
- [ ] Sistema de alertas
- [ ] Múltiples dispositivos
- [ ] App móvil
- [ ] Machine Learning para predicciones

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si quieres colaborar:

1. **Fork** el proyecto
2. Crea una **rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un **Pull Request**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE.md](LICENSE.md) para más detalles.

---

## 🔒 Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas certificados o credenciales al repositorio
- Usa el archivo `.gitignore` para proteger información sensible
- Rota tus certificados si fueron expuestos accidentalmente

---

## 📧 Soporte

¿Tienes preguntas o encontraste un bug?
- Abre un [Issue](../../issues)
- Revisa la [documentación del ESP32](./Esp32/README.md)

---

## 🙏 Agradecimientos

- [LilyGo](https://www.lilygo.cc/) - Hardware T-A7670
- [AWS IoT Core](https://aws.amazon.com/iot-core/) - Plataforma cloud
- [MicroPython](https://micropython.org/) - Firmware ESP32
- Comunidad IoT por el apoyo y recursos

---

<p align="center">
  <b>Hecho con ❤️ para la comunidad IoT</b><br>
  <sub>Un proyecto educativo de monitoreo ambiental</sub>
</p>
