# 📡 AWS IoT ESP32 Sensor Monitor

Proyecto IoT para monitoreo de **temperatura**, **humedad** y **calidad del aire** usando ESP32 con módulo LTE conectado a AWS IoT Core vía MQTT/TLS.

<p align="center">
  <img src="https://img.shields.io/badge/ESP32-MicroPython-blue?style=flat-square&logo=espressif" alt="ESP32">
  <img src="https://img.shields.io/badge/AWS-IoT_Core-orange?style=flat-square&logo=amazonaws" alt="AWS IoT">
  <img src="https://img.shields.io/badge/MQTT-TLS/SSL-green?style=flat-square" alt="MQTT">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

---

## 🔧 Hardware Utilizado

| Componente | Descripción |
|------------|-------------|
| **Microcontrolador** | LilyGo T-A7670 R2 (ESP32 + Módem A7670) |
| **Sensor de Temperatura/Humedad** | DHT22 (AM2302) |
| **Sensor de Calidad del Aire** | MQ135 (Gas/PPM) |
| **Conectividad** | LTE Cat-1 (2G/3G/4G) |
| **Protocolo** | MQTT sobre TLS 1.2 |

### 📌 Conexiones de Pines

```
DHT22  → GPIO 32
MQ135  → GPIO 33 (ADC)
LED    → GPIO 2 (indicador de estado)

Módem A7670:
  TX   → GPIO 26
  RX   → GPIO 27
  PWRKEY → GPIO 4
  DTR    → GPIO 25
  POWER  → GPIO 12
```

---

## ✨ Características

✅ Conexión a AWS IoT Core vía MQTT sobre SSL/TLS  
✅ Autenticación con certificados X.509  
✅ Publicación de datos cada 28 segundos (configurable)  
✅ Tiempo de conexión optimizado: **~4-5 minutos**  
✅ Reconexión automática en caso de fallo de red  
✅ Validación de configuración al iniciar  
✅ Indicadores LED de estado (conectando, éxito, error)  
✅ Manejo robusto de errores  

---

## 📋 Requisitos Previos

### 1️⃣ Hardware
- [LilyGo T-A7670 R2](https://www.lilygo.cc/products/t-sim-a7670e)
- Sensor DHT22
- Sensor MQ135
- Antena LTE
- SIM card con plan de datos

### 2️⃣ Software
- [MicroPython para ESP32](https://micropython.org/download/esp32/)
- [Thonny IDE](https://thonny.org/) o [ampy](https://github.com/scientifichackers/ampy)
- Cuenta de [AWS](https://aws.amazon.com/)

### 3️⃣ AWS IoT Core
- Thing creado en AWS IoT Core
- Certificados descargados (Root CA, Device Certificate, Private Key)
- Policy configurada con los siguientes permisos:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## ⚙️ Configuración

### 1. Configurar Credenciales

Edita el archivo `main.py` y completa las siguientes secciones:

#### 📶 Configuración de Red

```python
# CONFIGURA AQUÍ TU APN SEGÚN TU OPERADOR
APN = "web.colombiamovil.com.co"  # Ejemplo: Tigo Colombia
```

**APNs comunes en Colombia:**
- **Tigo**: `web.colombiamovil.com.co`
- **Claro**: `internet.comcel.com.co`
- **Movistar**: `internet.movistar.com.co`

#### ☁️ Configuración AWS IoT

```python
# CONFIGURA AQUÍ TU ENDPOINT DE AWS IoT
# Lo encuentras en: AWS IoT Core > Settings > Endpoint
AWS_ENDPOINT = "xxxxx-ats.iot.us-east-1.amazonaws.com"
```

#### 🔐 Certificados SSL/TLS

Pega tus certificados en las variables correspondientes:

1. **ROOT_CA**: Amazon Root CA 1  
   📥 [Descargar aquí](https://www.amazontrust.com/repository/AmazonRootCA1.pem)

2. **CERTIFICATE**: Certificado del dispositivo  
   📄 Archivo: `xxxxxxxxxx-certificate.pem.crt`

3. **PRIVATE_KEY**: Clave privada  
   🔑 Archivo: `xxxxxxxxxx-private.pem.key`

```python
ROOT_CA = """-----BEGIN CERTIFICATE-----
PEGA_AQUI_TU_ROOT_CA_CERTIFICATE
-----END CERTIFICATE-----"""

CERTIFICATE = """-----BEGIN CERTIFICATE-----
PEGA_AQUI_TU_DEVICE_CERTIFICATE
-----END CERTIFICATE-----"""

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
PEGA_AQUI_TU_PRIVATE_KEY
-----END RSA PRIVATE KEY-----"""
```

⚠️ **IMPORTANTE**: Nunca compartas estos certificados públicamente ni los subas a repositorios públicos.

---

## 🚀 Instalación y Uso

### Paso 1: Flashear MicroPython

```bash
# Descargar MicroPython para ESP32
wget https://micropython.org/resources/firmware/esp32-20230426-v1.20.0.bin

# Flashear (reemplaza /dev/ttyUSB0 con tu puerto)
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin
```

### Paso 2: Subir el código

**Opción A: Con Thonny**
1. Abre Thonny
2. Configura el intérprete a MicroPython (ESP32)
3. Abre `main.py`
4. Haz clic en "Save to Device" → Guarda como `main.py`

**Opción B: Con ampy**
```bash
pip install adafruit-ampy
ampy --port /dev/ttyUSB0 put main.py
```

### Paso 3: Ejecutar

El código se ejecutará automáticamente al reiniciar el ESP32, o manualmente:

```python
import main
main.main()
```

---

## 📊 Formato de Datos Publicados

El dispositivo publica datos en formato JSON al tópico `sensores`:

```json
{
  "device_id": "ESP32_SENSORES_a1b2c3d4",
  "contador": 1,
  "temperatura": 25.5,
  "humedad": 65.3,
  "ppm": 450.2
}
```

### Campos:
- `device_id`: ID único del dispositivo (basado en MAC)
- `contador`: Número secuencial de mensaje
- `temperatura`: Temperatura en °C (del DHT22)
- `humedad`: Humedad relativa en % (del DHT22)
- `ppm`: Partes por millón de gases (del MQ135)

---

## 🔍 Monitoreo y Depuración

### Verificar conexión MQTT en AWS

1. Ve a **AWS IoT Core** > **Test** > **MQTT test client**
2. Suscríbete al tópico: `sensores`
3. Deberías ver los mensajes llegando cada 28 segundos

### Logs del dispositivo

Conecta por puerto serial (115200 baudios) para ver los logs:

```bash
# En Linux/Mac
screen /dev/ttyUSB0 115200

# O con Thonny
# Ver > Shell
```

### Indicadores LED

| Patrón | Significado |
|--------|-------------|
| 🔵 Parpadeo rápido (5x) | ✅ Conexión exitosa |
| 🔴 Parpadeo lento (3x) | ❌ Error de conexión |
| 🟡 Parpadeo breve | 🔄 Conectando... |
| 💚 Pulso cada 1s | ✔️ Funcionando normalmente |

---

## 🛠️ Solución de Problemas

### ❌ "No se registró en la red"
- Verifica que la SIM tiene saldo/plan de datos
- Comprueba la señal LTE en tu ubicación
- Revisa que el APN sea correcto

### ❌ "Error conectando MQTT"
- Verifica que el endpoint de AWS IoT sea correcto
- Asegúrate de que los certificados estén completos (con BEGIN/END)
- Revisa que la Policy en AWS tenga permisos `iot:Connect` e `iot:Publish`
- Confirma que el Thing esté activo en AWS IoT Core

### ❌ "Certificados no configurados"
- Edita el código y pega tus certificados en las variables
- Asegúrate de mantener el formato con `-----BEGIN...` y `-----END...`

### ⚠️ Valores `null` en sensores
- **DHT22**: Verifica las conexiones y alimentación (3.3V o 5V)
- **MQ135**: El sensor necesita ~24-48h de "quemado" inicial

---

## 📝 Configuración Avanzada

### Cambiar intervalo de publicación

```python
PUBLISH_INTERVAL = 28000  # En milisegundos (28 segundos)
```

### Cambiar tópico MQTT

```python
TOPIC_PUB = "sensores/temperatura"  # Personaliza el tópico
```

### Ajustar pines

```python
DHT_PIN = 32   # Cambiar según tu conexión
MQ135_PIN = 33
```

---

## 📂 Estructura del Proyecto

```
aws-iot-esp32-sensors/
├── main.py              # Código principal
├── README.md            # Este archivo
├── .gitignore          # Archivos a ignorar
├── LICENSE             # Licencia MIT
└── docs/               # Documentación adicional
    ├── aws-setup.md    # Guía de configuración AWS
    └── wiring.md       # Diagramas de conexión
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si encuentras un bug o tienes una mejora:

1. Haz fork del proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [LilyGo](https://www.lilygo.cc/) por el hardware T-A7670
- [AWS IoT Core](https://aws.amazon.com/iot-core/) por la plataforma cloud
- Comunidad de [MicroPython](https://micropython.org/)

---

## 📧 Contacto

Si tienes preguntas o sugerencias, abre un [Issue](../../issues) en este repositorio.

---

<p align="center">
  Hecho con ❤️ para la comunidad IoT
</p>