#!/usr/bin/env python3
# ----------------------------------------------------------
# server.py
# ----------------------------------------------------------
# Servidor TCP que calcula el IMC (Índice de Masa Corporal)
# de forma remota. Escucha conexiones de clientes, recibe los
# datos del usuario (sexo, edad, altura y peso), calcula el IMC
# y devuelve el resultado en formato JSON.
#
# Autor: Julio Alberto Martinez Triana
# Fecha: 27/10/2025
# ----------------------------------------------------------

import socket      # Módulo para comunicación en red
import threading   # Para manejar múltiples clientes a la vez
import json        # Para enviar y recibir datos estructurados (JSON)

# ----------------------------------------------------------
# CONFIGURACIÓN DEL SERVIDOR
# ----------------------------------------------------------
HOST = '0.0.0.0'   # Escuchar en todas las interfaces disponibles
PORT = 5000        # Puerto TCP que usaremos para la comunicación

# ----------------------------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------------------------
def calcular_imc(peso, altura):
    """
    Calcula el Índice de Masa Corporal (IMC).
    Fórmula: IMC = peso / (altura ** 2)
    Retorna el IMC redondeado a 2 decimales.
    """
    if altura <= 0:
        raise ValueError("La altura debe ser mayor que 0.")
    imc = peso / (altura * altura)
    return round(imc, 2)

def clasificar_imc(imc):
    """
    Retorna la clasificación del IMC según el valor.
    """
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 25.0:
        return "Normal"
    elif imc < 30.0:
        return "Sobrepeso"
    else:
        return "Obesidad"

# ----------------------------------------------------------
# FUNCIÓN PRINCIPAL PARA ATENDER CLIENTES
# ----------------------------------------------------------
def manejar_cliente(conn, addr):
    """
    Atiende a un cliente conectado.
    Recibe datos en formato JSON, calcula el IMC
    y responde también en formato JSON.
    """
    print(f"[+] Nueva conexión desde {addr}")
    try:
        with conn:  # Contexto que cierra el socket automáticamente
            data = b''  # Buffer para acumular los datos recibidos

            while True:
                # Recibe bloques de datos del cliente
                chunk = conn.recv(4096)
                if not chunk:
                    break  # Si no hay más datos, cierra la conexión
                data += chunk

                # Los mensajes se delimitan con salto de línea '\n'
                if b'\n' in data:
                    linea, _, resto = data.partition(b'\n')
                    data = resto  # Mantiene lo que sobre para la siguiente lectura

                    # Decodifica el JSON recibido
                    try:
                        req = json.loads(linea.decode('utf-8'))
                    except Exception as e:
                        respuesta_err = {
                            "error": "Formato JSON inválido",
                            "detalle": str(e)
                        }
                        conn.sendall((json.dumps(respuesta_err) + '\n').encode('utf-8'))
                        continue

                    # Extrae los campos enviados por el cliente
                    try:
                        sexo = req.get("sexo")
                        edad = int(req.get("edad"))
                        altura = float(req.get("altura_m"))
                        peso = float(req.get("peso_kg"))
                    except Exception as e:
                        respuesta_err = {
                            "error": "Campos inválidos o faltantes",
                            "detalle": str(e)
                        }
                        conn.sendall((json.dumps(respuesta_err) + '\n').encode('utf-8'))
                        continue

                    # Calcula el IMC y genera la respuesta
                    try:
                        imc = calcular_imc(peso, altura)
                        clase = clasificar_imc(imc)
                        respuesta = {
                            "imc": imc,
                            "clasificacion": clase,
                            "mensaje": "IMC calculado correctamente"
                        }
                    except Exception as e:
                        respuesta = {
                            "error": "Error al calcular IMC",
                            "detalle": str(e)
                        }

                    # Envía la respuesta al cliente como JSON terminado en '\n'
                    conn.sendall((json.dumps(respuesta) + '\n').encode('utf-8'))

    except Exception as e:
        print(f"[!] Error con el cliente {addr}: {e}")
    finally:
        print(f"[-] Conexión cerrada {addr}")

# ----------------------------------------------------------
# FUNCIÓN PARA INICIAR EL SERVIDOR
# ----------------------------------------------------------
def iniciar_servidor():
    """
    Inicia el socket del servidor, lo asocia al puerto
    y queda escuchando conexiones de clientes.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permite reutilizar el puerto rápidamente si se reinicia el servidor
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        print(f"[+] Servidor escuchando en {HOST}:{PORT}")

        # Bucle infinito esperando clientes
        while True:
            conn, addr = s.accept()  # Espera una conexión
            # Crea un hilo para manejar a cada cliente sin bloquear a otros
            th = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            th.start()

# ----------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ----------------------------------------------------------
if __name__ == "__main__":
    iniciar_servidor()
