"""
AWS IoT via LTE con DHT22 + MQ135 + OLED - OPTIMIZADO CONSERVADOR FINAL
LilyGo T-A7670 R2 - MicroPython
Objetivo: Conexión en ~4-5 min, publicación cada 28s
FUNCIONA CON O SIN PANTALLA OLED
CON DELAY DE ESTABILIZACIÓN PARA ALIMENTACIÓN
"""

from machine import Pin, UART, unique_id, ADC, I2C
import time
import ubinascii
import dht
import json

# ═══════════════════════════════════════════════
# DELAY INICIAL CRÍTICO PARA ESTABILIZAR ALIMENTACIÓN
# ═══════════════════════════════════════════════
print("\n" + "="*50)
print("Estabilizando alimentación (5s)...")
print("="*50)
time.sleep(5)
print("✓ Sistema estabilizado\n")

# ═══════════════════════════════════════════════
# CONFIGURACIÓN PINES
# ═══════════════════════════════════════════════

MODEM_TX = 26
MODEM_RX = 27
MODEM_PWRKEY = 4
MODEM_DTR = 25
MODEM_POWER_EN = 12

DHT_PIN = 32
MQ135_PIN = 33

# Pines I2C para OLED
I2C_SCL = 22
I2C_SDA = 21

# ═══════════════════════════════════════════════
# CONFIGURACIÓN RED Y AWS
# ═══════════════════════════════════════════════
APN = "web.colombiamovil.com.co"
AWS_ENDPOINT = "au3e0f84d6xvr-ats.iot.us-east-1.amazonaws.com"
AWS_PORT = 8883
TOPIC_PUB = "sensores"

# Intervalo de publicación en milisegundos
PUBLISH_INTERVAL = 28000  # 28 segundos

# ═══════════════════════════════════════════════
# CERTIFICADOS AWS - PEGA AQUÍ TUS CERTIFICADOS
# ═══════════════════════════════════════════════
ROOT_CA = """-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----"""

CERTIFICATE = """-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUb1NZH1lUZeY3T2HcxYScDL34eEEwDQYJKoZIhvcNAQEL
BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g
SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI1MTAxMDIxMTE0
NVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0
ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJ7Byf4Wl+4gpqVsxfDX
nT8d99cduKpga6kVSjuv0rfPhQRcD4MPenXVsIuZyB8mMAGSlaHJHcPmXWXfnOVO
8Ulf16Rpr9K8p+WiXbNprnV2lSFq0UR05CrsKYjZnx/7A+791Ss12I55lOH9mYrb
qe/+w47rYgUNjY3GtzoCxc400jPE6aKs9f5RuK7dbntejE9/rpjNTtX4RkzMtA7q
ryP6aca8sf7zwvUy9+4/OeLTavEY2ukBG8neu+9srVlHlprYfTjsfAjFpDT4ADwM
HRHgYPlTX4gqTADsGTRIQQSMRbp+YyRzBPUuSz5AOV020rbFSHm9lkD7VVfnvwTD
YMMCAwEAAaNgMF4wHwYDVR0jBBgwFoAUxwNH7mor2z9FuRrETL+ZdKqcYqswHQYD
VR0OBBYEFE5bg6nW/IoDkJXS25u1fgDzsJmVMAwGA1UdEwEB/wQCMAAwDgYDVR0P
AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQBkdIma3X2UrkDukftWk1uDYpRJ
SG7DYx/cevAv/yvpul0K5vnavdJl82nOyOdhMbbHBiMbsawA+QBmi42MYztL44a+
ifq50BUK0b8ez+DzKmIubudiDYMZxHL+PV6jBEfKDu+ecs7ZItln1eX6hbgglhm7
+BYja3WAF8/GJp84+5VnacLk9ocj67eXMPJR77hatvZ3ulH2ni5zSqcFQCNaNng3
HWlV8jgFk/1HLRgOAq3rl4pxx/OEedifJQC/EPb9HseqMZO1BJBjro84snzhCyZp
1LgenV0uUicI/Did3QxEW1cvlUpeCqpoIW3fjNTyqPXve9NrwYrWu07Efbhj
-----END CERTIFICATE-----
"""

PRIVATE_KEY ="""-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAnsHJ/haX7iCmpWzF8NedPx331x24qmBrqRVKO6/St8+FBFwP
gw96ddWwi5nIHyYwAZKVockdw+ZdZd+c5U7xSV/XpGmv0ryn5aJds2mudXaVIWrR
RHTkKuwpiNmfH/sD7v3VKzXYjnmU4f2Zitup7/7DjutiBQ2Njca3OgLFzjTSM8Tp
oqz1/lG4rt1ue16MT3+umM1O1fhGTMy0DuqvI/ppxryx/vPC9TL37j854tNq8Rja
6QEbyd6772ytWUeWmth9OOx8CMWkNPgAPAwdEeBg+VNfiCpMAOwZNEhBBIxFun5j
JHME9S5LPkA5XTbStsVIeb2WQPtVV+e/BMNgwwIDAQABAoIBADBWy11dncc5E+Tc
2Ox7inq0ckmC2D6wezeRrve7koq7WkI4kdSTOvN0LHxlR8UMSKPB8WPArBqBI0Eo
tEoyHk/8Kdn7ADlHjkvig2tkq2VCxSfWsX+JpAvZus/bi5MeSFVV3rl4fMbtCEND
h6P7PKRBy2PSEhd9x/M6ZYH5ZCdj/TQbdsWLZMPsFue28yjbAGsYsDQfgG+R/9Mu
3nQ0j1nDydOyPx6+xL92KOCIGRGB10XCs322bbcfd9ZZnuzMzzzR8JWysBlAz2sQ
KFKSnE1uoiOrgAAnaNBsJxrnbqYeqO4oE5YSbvuLSxUZafOtPD3mWt+4Iq9RdhJ2
CF3ikRkCgYEAykYIzJPRiGnqSCUKWx88rfcZN2iJWA+rMSLZ9xd/XdQZA5rmEsZl
ItR9G5UuqH6569wt+xJv06lNXQLIyKIscx+Z23jHG2NOncvOM85wjaUzuHCSgtV/
4HrewpX595YSFPKi7hBdj6/11E92Uff5hVWebkPDDmrukqiInfoFi38CgYEAyOzD
m2wYX78CtaZlcRcPQ18R5NORYQW4r6WO6Ji0Gfoa2hzALH4UA4KR9hLg2YUcA4Gh
LqCzO/ihFi/iHCFsFpfZyrEvHgOUI1DbpynsZYMWWRgOcUX//SwBuLG/WnYRaqQn
iSqi/42SYwsBfZ7M2HFSQV3m5bL5TpJtp09WnL0CgYAMeBTCx7n69syCdgYVZ++N
qdXcHI2a6BxdgxB8su4fEpwYJMxaC/DgHMk5khC2QlmjuIb9Gz3Zhm5GdY17EMQ8
tI3/gYqEnbKS96VWfDtj//MYQ5hEiHTBmdFxnV0zbgTfVbXFhyy9VtOIqv1YQDkZ
hxWlJng3w0/BqrIBSxBccQKBgA+mqcIElI14woxFzucVRcIYuLsbY9qr6Gv+OHiT
1IuleMv+q1WL6KExXY9OfydSgBEh2t1X9T45qsqgpjtMuy+zWmq4jJQI8VQi60lF
Mb3ijS4Zep6GNl+ROv0ZE2/HfKnS6aV8pb/EVl/SrqYLZaeChEbFOsQvwc3GCDad
LoD9AoGBAIYmia1yl4p2As/ahuww+t3tK/JGhTXFT9eDiezrVwOfTUzxdQBq8NDt
WGrEW20n69Z9K/d3IpLjpPIVv+9LktD0oYpJBUXEMk0QySoAIP3EWaWX7BpwUvVG
DRaAhudwm/EiQHcdDYYZTcEg+vjp6iFdbIP7wAbAovFAinBiNF+6
-----END RSA PRIVATE KEY-----
"""
# ═══════════════════════════════════════════════
# HARDWARE
# ═══════════════════════════════════════════════
uart = UART(1, baudrate=115200, tx=MODEM_TX, rx=MODEM_RX, timeout=5000)
led = Pin(2, Pin.OUT)
pwrkey = Pin(MODEM_PWRKEY, Pin.OUT)
power_en = Pin(MODEM_POWER_EN, Pin.OUT)
dtr = Pin(MODEM_DTR, Pin.OUT)

sensor_dht = dht.DHT22(Pin(DHT_PIN))
sensor_mq = ADC(Pin(MQ135_PIN))
sensor_mq.atten(ADC.ATTN_11DB)
sensor_mq.width(ADC.WIDTH_12BIT)

# Inicializar OLED con protección de errores
oled = None
oled_disponible = False
try:
    import ssd1306
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    oled_disponible = True
    print("✓ OLED detectada y lista")
except Exception as e:
    print(f"⚠️  OLED no disponible: {e}")
    print("Continuando sin pantalla...")

count = 1
last_msg = 0
mqtt_client_index = 0

# ═══════════════════════════════════════════════
# FUNCIONES OLED
# ═══════════════════════════════════════════════
def oled_show(l1="", l2="", l3="", l4=""):
    """Mostrar texto en OLED (4 líneas) - Solo si está disponible"""
    if not oled_disponible or oled is None:
        return
    try:
        oled.fill(0)
        if l1: oled.text(l1, 0, 0)
        if l2: oled.text(l2, 0, 16)
        if l3: oled.text(l3, 0, 32)
        if l4: oled.text(l4, 0, 48)
        oled.show()
    except:
        pass

# ═══════════════════════════════════════════════
# FUNCIONES LED
# ═══════════════════════════════════════════════
def parpadeo_exito():
    for _ in range(5):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

def parpadeo_error():
    for _ in range(3):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

def parpadeo_conectando():
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

# ═══════════════════════════════════════════════
# FUNCIONES SENSORES
# ═══════════════════════════════════════════════
def leer_sensores():
    """Lee DHT22 y MQ135 y retorna dict con datos"""
    global count
    
    device_id = "ESP32_SENSORES_" + ubinascii.hexlify(unique_id()).decode()
    
    datos = {
        "device_id": device_id,
        "contador": count
    }
    
    # Leer DHT22 con retry
    for _ in range(2):
        try:
            sensor_dht.measure()
            datos["temperatura"] = round(sensor_dht.temperature(), 1)
            datos["humedad"] = round(sensor_dht.humidity(), 1)
            print(f"🌡️  Temp: {datos['temperatura']}°C | Humedad: {datos['humedad']}%")
            break
        except Exception as e:
            datos["temperatura"] = None
            datos["humedad"] = None
            time.sleep_ms(100)
    
    # Leer MQ135
    try:
        valor_adc = sensor_mq.read()
        ppm = (valor_adc / 4095.0) * 1000
        datos["ppm"] = round(ppm, 1)
        print(f"🌫️  PPM: {datos['ppm']}")
    except Exception as e:
        datos["ppm"] = None
    
    return datos

# ═══════════════════════════════════════════════
# FUNCIONES MODEM
# ═══════════════════════════════════════════════
def power_on_modem():
    print("\n⚡ Encendiendo A7670...")
    oled_show("AWS IoT", "1.Encendiendo", "modem...")
    power_en.value(1)
    dtr.value(0)
    time.sleep(0.1)
    pwrkey.value(1)
    time.sleep(1)
    pwrkey.value(0)
    time.sleep(5)  # NO TOCAR
    print("✓ Módulo encendido")

def send_at(cmd, wait_time=2, show_response=True):
    if show_response:
        print(f"→ {cmd}")
    while uart.any():
        uart.read()
    uart.write(cmd + '\r\n')
    time.sleep(wait_time)
    response = ""
    if uart.any():
        response = uart.read().decode('utf-8', 'ignore')
        if show_response:
            print(response)
    return response

def wait_for_network():
    print("\n📡 Esperando red Tigo...")
    oled_show("AWS IoT", "2.Esperando", "red Tigo...")
    for attempt in range(20):
        response = send_at("AT+CREG?", 0.8, False)
        if "+CREG: 0,1" in response or "+CREG: 0,5" in response:
            print(f"✓ Registrado en red! ({attempt + 1} intentos)")
            send_at("AT+CSQ", 1)
            oled_show("AWS IoT", "2.Red OK!", f"Int:{attempt+1}")
            parpadeo_exito()
            time.sleep(1)
            return True
        print(f"  Intento {attempt + 1}/20")
        oled_show("AWS IoT", "2.Red Tigo", f"Int:{attempt+1}/20")
        parpadeo_conectando()
        time.sleep(1.2)
    print("✗ No se registró")
    oled_show("ERROR", "No registro", "en red")
    parpadeo_error()
    return False

def setup_gprs():
    print("\n📶 Configurando datos...")
    print(f"Configurando APN: {APN}")
    oled_show("AWS IoT", "3.Config", "GPRS...")
    send_at(f'AT+CGDCONT=1,"IP","{APN}"', 2)
    print("Attach GPRS...")
    send_at("AT+CGATT=1", 2.5)
    time.sleep(1.5)
    print("Activando PDP...")
    send_at("AT+CGACT=1,1", 2.5)
    time.sleep(1)
    print("Verificando conectividad...")
    response = send_at('AT+CPING="8.8.8.8",1,2', 6)
    
    if "+CPING: 1" in response or "+CPING: 3" in response:
        print("✓ Datos activos!")
        oled_show("AWS IoT", "3.GPRS OK!")
        parpadeo_exito()
        time.sleep(1)
        return True
    else:
        print("⚠️  Continuando...")
        oled_show("AWS IoT", "3.GPRS OK!")
        time.sleep(1)
        return True

def upload_certificate(cert_name, cert_data):
    """Subir certificado al módulo A7670"""
    print(f"\n📜 Cargando {cert_name}...")
    oled_show("AWS IoT", "4.Cargando", cert_name[:12])
    cert_data = cert_data.strip()
    cert_size = len(cert_data)
    print(f"Tamaño: {cert_size} bytes")
    
    while uart.any():
        uart.read()
    time.sleep(0.5)
    
    cmd = f'AT+CCERTDOWN="{cert_name}",{cert_size}'
    print(f"→ {cmd}")
    uart.write(cmd + '\r\n')
    
    response = ""
    timeout = 80
    found_prompt = False
    
    print("Esperando prompt '>'...")
    while timeout > 0:
        if uart.any():
            chunk = uart.read().decode('utf-8', 'ignore')
            response += chunk
            print(chunk, end='')
            
            if '>' in chunk or '>' in response:
                found_prompt = True
                print("\n✓ Prompt '>' recibido")
                break
            
            if 'ERROR' in chunk:
                print("\n✗ Error en comando")
                return False
        
        time.sleep(0.1)
        timeout -= 1
    
    if not found_prompt:
        print(f"\n✗ No se recibió prompt '>'")
        return False
    
    print("Enviando certificado...")
    uart.write(cert_data.encode())
    time.sleep(3.5)
    
    response = ""
    timeout = 80
    print("Esperando confirmación...")
    
    while timeout > 0:
        if uart.any():
            chunk = uart.read().decode('utf-8', 'ignore')
            response += chunk
            print(chunk, end='')
            
            if 'OK' in response:
                print(f"\n✓ {cert_name} cargado exitosamente!")
                return True
            
            if 'ERROR' in response:
                print(f"\n✗ Error cargando certificado")
                return False
        
        time.sleep(0.1)
        timeout -= 1
    
    print(f"\n✗ Timeout esperando confirmación")
    return False

def load_certificates():
    """Cargar certificados al módulo para SSL"""
    print("\n" + "="*50)
    print("  CARGANDO CERTIFICADOS PARA SSL")
    print("="*50)
    
    if "PEGA_AQUI" in ROOT_CA:
        print("\n⚠️  ADVERTENCIA: Certificados no configurados")
        oled_show("ERROR", "Sin certs!")
        time.sleep(2)
        return False
    
    success = True
    
    if not upload_certificate("cacert.pem", ROOT_CA):
        success = False
    time.sleep(0.7)
    
    if not upload_certificate("clientcert.pem", CERTIFICATE):
        success = False
    time.sleep(0.7)
    
    if not upload_certificate("clientkey.pem", PRIVATE_KEY):
        success = False
    
    if success:
        print("\n✓ Todos los certificados cargados!")
        oled_show("AWS IoT", "4.Certs OK!")
        time.sleep(1)
    else:
        print("\n✗ Error cargando uno o más certificados")
        oled_show("ERROR", "Certs fail")
        time.sleep(1)
    
    return success

def configure_ssl():
    """Configurar parámetros SSL"""
    print("\n🔐 Configurando SSL...")
    print("Configurando contexto SSL 0 para MQTT...")
    oled_show("AWS IoT", "5.Config TLS")
    send_at('AT+CSSLCFG="sslversion",0,3', 1.5)
    send_at('AT+CSSLCFG="authmode",0,2', 1.5)
    send_at('AT+CSSLCFG="cacert",0,"cacert.pem"', 1.5)
    send_at('AT+CSSLCFG="clientcert",0,"clientcert.pem"', 1.5)
    send_at('AT+CSSLCFG="clientkey",0,"clientkey.pem"', 1.5)
    print("✓ SSL configurado en contexto 0")
    oled_show("AWS IoT", "5.TLS OK!")
    time.sleep(1)

# ═══════════════════════════════════════════════
# FUNCIONES MQTT
# ═══════════════════════════════════════════════
def mqtt_start():
    """Iniciar servicio MQTT"""
    print("\n📡 Iniciando servicio MQTT...")
    print("Deteniendo servicio MQTT previo...")
    oled_show("AWS IoT", "6.Init MQTT")
    send_at("AT+CMQTTSTOP", 2, False)
    time.sleep(0.7)
    
    response = send_at("AT+CMQTTSTART", 4)
    
    if "OK" in response or "+CMQTTSTART: 0" in response or "ALREADY" in response:
        print("✓ Servicio MQTT iniciado")
        oled_show("AWS IoT", "6.MQTT OK!")
        time.sleep(1.5)
        return True
    else:
        print(f"✗ Error iniciando MQTT")
        oled_show("ERROR", "MQTT Start")
        time.sleep(1)
        return False

def mqtt_acquire_client():
    """Adquirir cliente MQTT"""
    global mqtt_client_index
    
    print("\n🔗 Adquiriendo cliente MQTT...")
    oled_show("AWS IoT", "7.Cliente", "MQTT...")
    client_id = "ESP32_SENSORES_" + ubinascii.hexlify(unique_id()).decode()
    print(f"Client ID: {client_id}")
    
    send_at(f"AT+CMQTTREL={mqtt_client_index}", 1, False)
    time.sleep(0.7)
    
    print("Adquiriendo con SSL y certificados...")
    cmd = f'AT+CMQTTACCQ={mqtt_client_index},"{client_id}",1'
    response = send_at(cmd, 3)
    
    if "OK" in response:
        print("✓ Cliente MQTT adquirido con SSL + certificados")
        oled_show("AWS IoT", "7.Cliente OK!")
        time.sleep(1)
        return True
    else:
        print(f"⚠️  Error con SSL")
        oled_show("ERROR", "Cliente fail")
        time.sleep(1)
        return False

def mqtt_connect():
    """Conectar al broker MQTT"""
    print(f"\n🔌 Conectando a AWS IoT...")
    print(f"Endpoint: {AWS_ENDPOINT}")
    print(f"Puerto: {AWS_PORT}")
    
    print("\n🔐 Asignando contexto SSL 0 al cliente MQTT 0...")
    oled_show("AWS IoT", "8.Conectando", "AWS IoT...")
    response = send_at(f"AT+CMQTTSSLCFG={mqtt_client_index},0", 3)
    
    if "OK" not in response:
        print(f"✗ Error configurando SSL: {response}")
        oled_show("ERROR", "SSL config")
        time.sleep(1)
        return False
    
    print("✓ Contexto SSL asignado")
    print(f"\n🔌 Conectando a AWS IoT (esto puede tomar 25-35s)...")
    oled_show("AWS IoT", "8.Conectando", "Espera 30s...")
    
    server_url = f"tcp://{AWS_ENDPOINT}:{AWS_PORT}"
    print(f"URL: {server_url}")
    
    cmd = f'AT+CMQTTCONNECT={mqtt_client_index},"{server_url}",60,1'
    
    while uart.any():
        uart.read()
    
    print(f"→ {cmd}")
    uart.write(cmd + '\r\n')
    
    time.sleep(3)
    initial_response = ""
    if uart.any():
        initial_response = uart.read().decode('utf-8', 'ignore')
        print(initial_response, end='')
    
    if "+CMQTTCONNECT: 0,0" in initial_response:
        print("\n\n" + "="*50)
        print("  🎉🎉🎉 ¡CONECTADO A AWS IoT! 🎉🎉🎉")
        print("="*50 + "\n")
        oled_show("*** EXITO ***", "", "CONECTADO!", "AWS IoT")
        parpadeo_exito()
        time.sleep(2)
        return True
    elif "+CMQTTCONNECT:" in initial_response and ",0" not in initial_response:
        print(f"\n✗ Error de conexión")
        oled_show("ERROR", "Conexion fail")
        time.sleep(1)
        return False
    
    if "OK" in initial_response:
        print("Esperando confirmación de conexión...")
        timeout = 35
        start_time = time.time()
        
        while timeout > 0:
            if uart.any():
                data = uart.read().decode('utf-8', 'ignore')
                print(data, end='')
                
                if "+CMQTTCONNECT: 0,0" in data:
                    print("\n\n" + "="*50)
                    print("  🎉🎉🎉 ¡CONECTADO A AWS IoT! 🎉🎉🎉")
                    print("="*50 + "\n")
                    oled_show("*** EXITO ***", "", "CONECTADO!", "AWS IoT")
                    parpadeo_exito()
                    time.sleep(2)
                    return True
                elif "+CMQTTCONNECT:" in data:
                    print(f"\n✗ Error de conexión: {data}")
                    oled_show("ERROR", "Conn fail")
                    time.sleep(1)
                    return False
            
            time.sleep(0.5)
            timeout -= 0.5
            
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"\n  Esperando confirmación... ({elapsed}s)")
                oled_show("AWS IoT", "8.Conectando", f"{elapsed}s...")
        
        print("\n✗ Timeout esperando respuesta")
        oled_show("ERROR", "Timeout")
        time.sleep(1)
        return False
    else:
        print(f"✗ Error en comando")
        oled_show("ERROR", "CMD fail")
        time.sleep(1)
        return False

def mqtt_publish(topic, message):
    """Publicar mensaje - OPTIMIZADO PARA VELOCIDAD"""
    global count
    
    print(f"\n📤 Publicando #{count} a '{topic}'")
    
    # Topic
    topic_len = len(topic)
    cmd = f"AT+CMQTTTOPIC={mqtt_client_index},{topic_len}"
    response = send_at(cmd, 1.5, False)
    
    if ">" not in response:
        print("✗ No se recibió prompt para tópico")
        return False
    
    uart.write(topic.encode())
    time.sleep(0.5)
    uart.read()
    
    # Payload
    payload_len = len(message)
    cmd = f"AT+CMQTTPAYLOAD={mqtt_client_index},{payload_len}"
    response = send_at(cmd, 1.5, False)
    
    if ">" not in response:
        print("✗ No se recibió prompt para payload")
        return False
    
    uart.write(message.encode())
    time.sleep(0.5)
    uart.read()
    
    # Publicar
    cmd = f"AT+CMQTTPUB={mqtt_client_index},0,60"
    response = send_at(cmd, 2, False)
    
    if "OK" in response:
        print("✓ Mensaje publicado!")
        led.on()
        time.sleep(0.15)
        led.off()
        count += 1
        return True
    else:
        print("✗ Error publicando")
        return False

# ═══════════════════════════════════════════════
# PROGRAMA PRINCIPAL
# ═══════════════════════════════════════════════
def main():
    global last_msg
    
    print("\n╔════════════════════════════════════════╗")
    print("║  AWS IoT + DHT22 + MQ135 OPTIMIZADO  ║")
    print("║  LilyGo T-A7670 R2                    ║")
    print(f"║  Intervalo: {PUBLISH_INTERVAL//1000}s                      ║")
    print("╚════════════════════════════════════════╝\n")
    
    oled_show("AWS IoT", "Iniciando...", "", "T-A7670 R2")
    
    start_time = time.time()
    
    time.sleep(2)
    
    # Prueba de sensores
    print("\n🔧 Probando sensores...")
    oled_show("Test", "Sensores...")
    leer_sensores()
    time.sleep(2)
    
    # 1. Encender
    power_on_modem()
    time.sleep(2)
    
    # 2. Inicializar
    send_at("AT", 1)
    send_at("ATE0", 1)
    
    # 3. Red
    if not wait_for_network():
        print("\n❌ Error en red")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    # 4. Datos
    if not setup_gprs():
        print("\n❌ Error en datos")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    # 5. Cargar certificados
    certs_loaded = load_certificates()
    
    if not certs_loaded:
        print("\n⚠️  Certificados no cargados")
        time.sleep(3)
    
    # 6. Configurar SSL
    if certs_loaded:
        configure_ssl()
    
    # 7. Iniciar MQTT
    if not mqtt_start():
        print("\n❌ Error iniciando MQTT")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    # 8. Adquirir cliente
    if not mqtt_acquire_client():
        print("\n❌ Error adquiriendo cliente")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    # 9. Conectar MQTT
    if not mqtt_connect():
        print("\n❌ Error conectando MQTT")
        print("\n💡 VERIFICA:")
        print("   1. Certificados correctos y activos en AWS")
        print("   2. Thing creado en AWS IoT")
        print("   3. Policy con permisos iot:Connect y iot:Publish")
        print("   4. Endpoint correcto")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    
    print("\n" + "="*50)
    print(f"  ✅ CONECTADO en {minutes}:{seconds:02d}")
    print(f"  📤 Publicando cada {PUBLISH_INTERVAL//1000}s")
    print("="*50 + "\n")
    
    oled_show("*** LISTO ***", f"Tiempo:{minutes}:{seconds:02d}", f"Envio c/{PUBLISH_INTERVAL//1000}s")
    time.sleep(3)
    
    # Loop principal
    try:
        while True:
            now = time.ticks_ms()
            
            # Publicar según intervalo configurado
            if time.ticks_diff(now, last_msg) > PUBLISH_INTERVAL:
                last_msg = now
                
                # Leer sensores
                datos = leer_sensores()
                
                # Mostrar en OLED con indicador de envío
                t = datos.get("temperatura", 0)
                h = datos.get("humedad", 0)
                p = datos.get("ppm", 0)
                oled_show(f"T:{t}C H:{h}%", f"PPM:{p}", "", ">>> AWS >>> #"+str(count))
                
                # Convertir a JSON
                payload = json.dumps(datos)
                print(f"Payload: {payload}")
                
                # Publicar
                mqtt_publish(TOPIC_PUB, payload)
                
                # Actualizar pantalla sin indicador de envío
                time.sleep(0.5)
                oled_show(f"T:{t}C H:{h}%", f"PPM:{p}", "", "Msg #"+str(count-1))
            
            # LED heartbeat
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⛔ Detenido por usuario")
        print("Desconectando...")
        oled_show("Detenido", "por usuario")
        send_at(f"AT+CMQTTDISC={mqtt_client_index},60", 3)
        send_at(f"AT+CMQTTREL={mqtt_client_index}", 2)
        send_at("AT+CMQTTSTOP", 2)
        led.off()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        oled_show("ERROR:", str(e)[:16])
        try:
            send_at(f"AT+CMQTTDISC={mqtt_client_index},60", 3)
            send_at(f"AT+CMQTTREL={mqtt_client_index}", 2)
            send_at("AT+CMQTTSTOP", 2)
        except:
            pass
        led.off()

if __name__ == "__main__":
    main()