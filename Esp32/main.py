"""
AWS IoT via LTE con DHT22 + MQ135 - OPTIMIZADO CONSERVADOR FINAL
LilyGo T-A7670 R2 - MicroPython
Objetivo: Conexión en ~4-5 min, publicación cada 28s

IMPORTANTE: Antes de usar, configura tus credenciales en la sección de CONFIGURACIÓN
"""

from machine import Pin, UART, unique_id, ADC
import time
import ubinascii
import dht
import json

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

# ═══════════════════════════════════════════════
# CONFIGURACIÓN RED Y AWS
# ═══════════════════════════════════════════════
# CONFIGURA AQUÍ TU APN SEGÚN TU OPERADOR
# Ejemplos:
# - Tigo Colombia: "web.colombiamovil.com.co"
# - Claro Colombia: "internet.comcel.com.co"
# - Movistar Colombia: "internet.movistar.com.co"
APN = "TU_APN_AQUI"

# CONFIGURA AQUÍ TU ENDPOINT DE AWS IoT
# Lo encuentras en: AWS IoT Core > Settings > Endpoint
# Ejemplo: "xxxxx-ats.iot.us-east-1.amazonaws.com"
AWS_ENDPOINT = "TU_ENDPOINT_AWS_IOT_AQUI"

AWS_PORT = 8883

# CONFIGURA AQUÍ EL TÓPICO MQTT DONDE PUBLICARÁS
TOPIC_PUB = "sensores"

# Intervalo de publicación en milisegundos
PUBLISH_INTERVAL = 28000  # 28 segundos

# ═══════════════════════════════════════════════
# CERTIFICADOS AWS IoT Core
# ═══════════════════════════════════════════════
# IMPORTANTE: Obtén estos certificados desde tu consola de AWS IoT Core
# 
# 1. ROOT_CA: Amazon Root CA 1
#    Descarga desde: https://www.amazontrust.com/repository/AmazonRootCA1.pem
#
# 2. CERTIFICATE: Certificado de tu dispositivo (Thing)
#    Lo descargas al crear el Thing en AWS IoT Core
#    Archivo: xxxxxxxxxx-certificate.pem.crt
#
# 3. PRIVATE_KEY: Clave privada de tu dispositivo
#    Lo descargas al crear el Thing en AWS IoT Core
#    Archivo: xxxxxxxxxx-private.pem.key
#
# ⚠️  NUNCA compartas estos certificados públicamente
# ═══════════════════════════════════════════════

ROOT_CA = """-----BEGIN CERTIFICATE-----
PEGA_AQUI_TU_ROOT_CA_CERTIFICATE
Debe comenzar con -----BEGIN CERTIFICATE-----
y terminar con -----END CERTIFICATE-----
-----END CERTIFICATE-----"""

CERTIFICATE = """-----BEGIN CERTIFICATE-----
PEGA_AQUI_TU_DEVICE_CERTIFICATE
Debe comenzar con -----BEGIN CERTIFICATE-----
y terminar con -----END CERTIFICATE-----
-----END CERTIFICATE-----
"""

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
PEGA_AQUI_TU_PRIVATE_KEY
Debe comenzar con -----BEGIN RSA PRIVATE KEY-----
y terminar con -----END RSA PRIVATE KEY-----
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

count = 1
last_msg = 0
mqtt_client_index = 0

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
    print("\n📡 Esperando red celular...")
    for attempt in range(20):  # 20 intentos
        response = send_at("AT+CREG?", 0.8, False)
        if "+CREG: 0,1" in response or "+CREG: 0,5" in response:
            print(f"✓ Registrado en red! ({attempt + 1} intentos)")
            send_at("AT+CSQ", 1)
            parpadeo_exito()
            return True
        print(f"  Intento {attempt + 1}/20")
        parpadeo_conectando()
        time.sleep(1.2)
    print("✗ No se registró")
    parpadeo_error()
    return False

def setup_gprs():
    print("\n📶 Configurando datos...")
    print(f"Configurando APN: {APN}")
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
        parpadeo_exito()
        return True
    else:
        print("⚠️  Continuando...")
        return True

def upload_certificate(cert_name, cert_data):
    """Subir certificado al módulo A7670"""
    print(f"\n📜 Cargando {cert_name}...")
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
        print("    Por favor, edita el archivo y pega tus certificados")
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
    else:
        print("\n✗ Error cargando uno o más certificados")
    
    return success

def configure_ssl():
    """Configurar parámetros SSL"""
    print("\n🔐 Configurando SSL...")
    print("Configurando contexto SSL 0 para MQTT...")
    send_at('AT+CSSLCFG="sslversion",0,3', 1.5)
    send_at('AT+CSSLCFG="authmode",0,2', 1.5)
    send_at('AT+CSSLCFG="cacert",0,"cacert.pem"', 1.5)
    send_at('AT+CSSLCFG="clientcert",0,"clientcert.pem"', 1.5)
    send_at('AT+CSSLCFG="clientkey",0,"clientkey.pem"', 1.5)
    print("✓ SSL configurado en contexto 0")

# ═══════════════════════════════════════════════
# FUNCIONES MQTT
# ═══════════════════════════════════════════════
def mqtt_start():
    """Iniciar servicio MQTT"""
    print("\n📡 Iniciando servicio MQTT...")
    print("Deteniendo servicio MQTT previo...")
    send_at("AT+CMQTTSTOP", 2, False)
    time.sleep(0.7)
    
    response = send_at("AT+CMQTTSTART", 4)
    
    if "OK" in response or "+CMQTTSTART: 0" in response or "ALREADY" in response:
        print("✓ Servicio MQTT iniciado")
        time.sleep(1.5)
        return True
    else:
        print(f"✗ Error iniciando MQTT")
        return False

def mqtt_acquire_client():
    """Adquirir cliente MQTT"""
    global mqtt_client_index
    
    print("\n🔗 Adquiriendo cliente MQTT...")
    client_id = "ESP32_SENSORES_" + ubinascii.hexlify(unique_id()).decode()
    print(f"Client ID: {client_id}")
    
    send_at(f"AT+CMQTTREL={mqtt_client_index}", 1, False)
    time.sleep(0.7)
    
    print("Adquiriendo con SSL y certificados...")
    cmd = f'AT+CMQTTACCQ={mqtt_client_index},"{client_id}",1'
    response = send_at(cmd, 3)
    
    if "OK" in response:
        print("✓ Cliente MQTT adquirido con SSL + certificados")
        return True
    else:
        print(f"⚠️  Error con SSL")
        return False

def mqtt_connect():
    """Conectar al broker MQTT"""
    print(f"\n🔌 Conectando a AWS IoT...")
    print(f"Endpoint: {AWS_ENDPOINT}")
    print(f"Puerto: {AWS_PORT}")
    
    print("\n🔐 Asignando contexto SSL 0 al cliente MQTT 0...")
    response = send_at(f"AT+CMQTTSSLCFG={mqtt_client_index},0", 3)
    
    if "OK" not in response:
        print(f"✗ Error configurando SSL: {response}")
        return False
    
    print("✓ Contexto SSL asignado")
    print(f"\n🔌 Conectando a AWS IoT (esto puede tomar 25-35s)...")
    
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
        parpadeo_exito()
        return True
    elif "+CMQTTCONNECT:" in initial_response and ",0" not in initial_response:
        print(f"\n✗ Error de conexión")
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
                    parpadeo_exito()
                    return True
                elif "+CMQTTCONNECT:" in data:
                    print(f"\n✗ Error de conexión: {data}")
                    return False
            
            time.sleep(0.5)
            timeout -= 0.5
            
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"\n  Esperando confirmación... ({elapsed}s)")
        
        print("\n✗ Timeout esperando respuesta")
        return False
    else:
        print(f"✗ Error en comando")
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
    
    # Validar configuración
    if "PEGA_AQUI" in ROOT_CA or "TU_" in AWS_ENDPOINT or "TU_" in APN:
        print("\n❌ ERROR: Configuración incompleta")
        print("Por favor, edita las siguientes variables en el código:")
        if "TU_" in APN:
            print("  - APN: Configura el APN de tu operador")
        if "TU_" in AWS_ENDPOINT:
            print("  - AWS_ENDPOINT: Configura tu endpoint de AWS IoT")
        if "PEGA_AQUI" in ROOT_CA:
            print("  - ROOT_CA, CERTIFICATE, PRIVATE_KEY: Pega tus certificados")
        print("\n⛔ Deteniendo programa...")
        while True:
            parpadeo_error()
            time.sleep(2)
    
    start_time = time.time()
    
    time.sleep(2)
    
    # Prueba de sensores
    print("\n🔧 Probando sensores...")
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
    
    # Loop principal
    try:
        while True:
            now = time.ticks_ms()
            
            # Publicar según intervalo configurado
            if time.ticks_diff(now, last_msg) > PUBLISH_INTERVAL:
                last_msg = now
                
                # Leer sensores
                datos = leer_sensores()
                
                # Convertir a JSON
                payload = json.dumps(datos)
                print(f"Payload: {payload}")
                
                # Publicar
                mqtt_publish(TOPIC_PUB, payload)
            
            # LED heartbeat
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⛔ Detenido por usuario")
        print("Desconectando...")
        send_at(f"AT+CMQTTDISC={mqtt_client_index},60", 3)
        send_at(f"AT+CMQTTREL={mqtt_client_index}", 2)
        send_at("AT+CMQTTSTOP", 2)
        led.off()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            send_at(f"AT+CMQTTDISC={mqtt_client_index},60", 3)
            send_at(f"AT+CMQTTREL={mqtt_client_index}", 2)
            send_at("AT+CMQTTSTOP", 2)
        except:
            pass
        led.off()

if __name__ == "__main__":
    main()