# 🛰️ Proyecto de Comunicación Cliente-Servidor con Python (TCP)

Este proyecto demuestra cómo implementar una comunicación **cliente-servidor** usando **sockets TCP** en Python, además de cómo **capturar y analizar el tráfico de red** generado con **Scapy** y **Wireshark**.  

---

## 📋 Contenido

- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Ejemplo de ejecución local (loopback)](#-ejemplo-de-ejecución-local-loopback)
- [Configuración para ejecutar en diferentes máquinas](#-configuración-para-ejecutar-en-diferentes-máquinas)
- [Captura de tráfico con Scapy](#-captura-de-tráfico-con-scapy)
- [Análisis de tráfico en Wireshark](#-análisis-de-tráfico-en-wireshark)
- [Notas técnicas](#-notas-técnicas)
- [Posibles errores y soluciones](#-posibles-errores-y-soluciones)

---

## 🧩 Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Python 3.8+**
- **Pip**
- **Wireshark** (para análisis de paquetes)
- **Scapy** para Python

Puedes instalar Scapy ejecutando:

```bash
pip install scapy
```

---

## 📁 Estructura del proyecto

```bash
cliente_servidor_tcp/
│
├── servidor.py
├── cliente.py
├── capturar_paquetes.py
└── README.md
```

---

## ⚙️ Instalación

Clona este repositorio o copia los archivos en una carpeta local:

```bash
git clone https://github.com/tuusuario/cliente_servidor_tcp.git
cd cliente_servidor_tcp
```

---

## 💻 Ejemplo de ejecución local (loopback)

Este ejemplo usa el **localhost (127.0.0.1)**, por lo que tanto el cliente como el servidor se ejecutan **en la misma máquina**.

### 1️⃣ Servidor (`servidor.py`)

```python
import socket

# Crear socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 5000))
server_socket.listen(1)
print("Servidor escuchando en 127.0.0.1:5000")

conn, addr = server_socket.accept()
print(f"Conexión establecida desde: {addr}")

while True:
    data = conn.recv(1024).decode()
    if not data or data.lower() == 'exit':
        print("Cliente desconectado")
        break
    print(f"Cliente dice: {data}")
    conn.send("Mensaje recibido".encode())

conn.close()
```

---

### 2️⃣ Cliente (`cliente.py`)

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5000))
print("Conectado al servidor")

while True:
    msg = input("Mensaje para el servidor ('exit' para salir): ")
    client_socket.send(msg.encode())
    if msg.lower() == 'exit':
        break
    respuesta = client_socket.recv(1024).decode()
    print(f"Servidor responde: {respuesta}")

client_socket.close()
```

---

## 🌐 Configuración para ejecutar en diferentes máquinas

Si tienes el **servidor** en una máquina y el **cliente** en otra, sigue estos pasos:

### 🧠 Paso 1. Verifica la IP del servidor

En la máquina del servidor, abre una terminal y ejecuta:

```bash
ipconfig
```

Busca tu adaptador de red activo (Wi-Fi o Ethernet) y anota la **dirección IPv4** (por ejemplo, `192.168.1.100`).

---

### 🧠 Paso 2. Modifica el código

En el archivo `servidor.py`, cambia:

```python
server_socket.bind(('127.0.0.1', 5000))
```

por:

```python
server_socket.bind(('0.0.0.0', 5000))
```

Esto hace que el servidor escuche en **todas las interfaces de red**.

En el archivo `cliente.py`, reemplaza:

```python
client_socket.connect(('127.0.0.1', 5000))
```

por:

```python
client_socket.connect(('192.168.1.100', 5000))
```

(donde `192.168.1.100` es la IP real del servidor).

---

### 🧠 Paso 3. Verifica el firewall

Asegúrate de permitir el puerto **5000 TCP** en el firewall del servidor:

- Abre *Panel de Control → Sistema y Seguridad → Firewall de Windows → Configuración avanzada*  
- Agrega una **regla de entrada** para permitir el puerto `5000` en TCP.

---

### 🧠 Paso 4. Conecta

Primero, ejecuta el **servidor**:

```bash
python servidor.py
```

Luego, en la máquina cliente:

```bash
python cliente.py
```

¡Listo! El cliente y el servidor ahora pueden comunicarse entre sí a través de la red local.

---

## 📡 Captura de tráfico con Scapy

Puedes capturar los paquetes generados con el siguiente script:

### `capturar_paquetes.py`

```python
from scapy.all import sniff

def packet_callback(packet):
    print(packet.summary())

# Cambia iface="Wi-Fi" o "Ethernet" según tu red
sniff(iface="Wi-Fi", prn=packet_callback, count=50)
```

Este código escucha los primeros **50 paquetes** en la interfaz de red seleccionada e imprime un resumen por consola.

> ⚠️ Si lo ejecutas con `iface="Adapter for loopback traffic capture"`, solo verás el tráfico interno (127.0.0.1).

---

## 🔬 Análisis de tráfico en Wireshark

Puedes analizar las comunicaciones de tu cliente y servidor con **Wireshark**:

1. Abre **Wireshark**.  
2. Elige la interfaz:
   - Si estás usando el mismo PC: selecciona `Adapter for loopback traffic capture`
   - Si estás usando dos máquinas: selecciona `Wi-Fi` o `Ethernet`, según corresponda.
3. En el filtro superior, escribe:
   ```
   tcp.port == 5000
   ```
   Así solo verás los paquetes de tu implementación.
4. Inicia el servidor y luego el cliente.
5. Observa cómo se crean los paquetes TCP con flags como:
   - **SYN** → solicitud de conexión
   - **ACK** → acuse de recibo
   - **PSH** → envío de datos
   - **FIN** → cierre de conexión

---

## 🧠 Notas técnicas

- **Protocolo usado:** TCP (orientado a conexión)
- **Puerto usado:** 5000 (puede cambiarse libremente)
- **Codificación:** UTF-8
- **Loopback (127.0.0.1):** se usa solo para pruebas locales
- **`0.0.0.0`:** indica que el servidor escucha en todas las interfaces
- **`socket.AF_INET`:** indica IPv4
- **`socket.SOCK_STREAM`:** define que se usa TCP

---

## ⚠️ Posibles errores y soluciones

| Problema | Causa | Solución |
|-----------|--------|----------|
| `ConnectionRefusedError` | El servidor no está corriendo o el puerto está cerrado | Asegúrate de iniciar el servidor primero y abrir el puerto 5000 |
| `OSError: [WinError 10048]` | Puerto en uso | Cambia el puerto, por ejemplo a 5001 |
| No se ven paquetes en Wireshark | Estás capturando en interfaz incorrecta | Selecciona `Wi-Fi` o `Ethernet`, no loopback |
| Cliente no conecta desde otra máquina | Firewall o IP incorrecta | Desactiva temporalmente el firewall o revisa la IP con `ipconfig` |

---

## 📘 Ejemplo de flujo TCP visto en Wireshark

Cuando todo está funcionando, deberías ver algo así en Wireshark:

| Source | Destination | Protocol | Info |
|--------|--------------|-----------|------|
| 192.168.1.5 | 192.168.1.10 | TCP | SYN, conexión inicial |
| 192.168.1.10 | 192.168.1.5 | TCP | SYN, ACK |
| 192.168.1.5 | 192.168.1.10 | TCP | PSH, ACK, datos enviados |
| 192.168.1.10 | 192.168.1.5 | TCP | ACK |
| 192.168.1.5 | 192.168.1.10 | TCP | FIN, cierre de conexión |

---

## 🧩 Autor
Julio Martinez Triana

Proyecto desarrollado por **[Tu Nombre]** como demostración educativa del modelo **Cliente-Servidor TCP** con Python y análisis de red con **Wireshark** y **Scapy**.
