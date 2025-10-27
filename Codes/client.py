#!/usr/bin/env python3
# ----------------------------------------------------------
# client.py
# ----------------------------------------------------------
# Cliente TCP que solicita al usuario los datos necesarios
# para calcular el IMC, los envía al servidor y muestra el
# resultado recibido en formato JSON.
#
# Autor: Julio Alberto Martinez Triana
# Fecha: 27/10/2025
# ----------------------------------------------------------

import socket  # Comunicación TCP/IP
import json    # Formato de datos intercambiados

# ----------------------------------------------------------
# CONFIGURACIÓN DEL CLIENTE
# ----------------------------------------------------------
SERVER_HOST = '127.0.0.1'  # IP del servidor (usa localhost si está en la misma PC)
SERVER_PORT = 5000         # Puerto que usa el servidor

# ----------------------------------------------------------
# FUNCIÓN PARA PEDIR LOS DATOS AL USUARIO
# ----------------------------------------------------------
def pedir_datos():
    """
    Solicita al usuario los datos necesarios para calcular el IMC.
    Retorna un diccionario con los valores.
    """
    print("=== CÁLCULO REMOTO DEL IMC ===")
    sexo = input("Sexo (M/F): ").strip()
    edad = input("Edad (años): ").strip()
    altura = input("Altura (metros, ej: 1.75): ").strip()
    peso = input("Peso (kg): ").strip()
    return {
        "sexo": sexo,
        "edad": edad,
        "altura_m": altura,
        "peso_kg": peso
    }

# ----------------------------------------------------------
# FUNCIÓN PRINCIPAL DEL CLIENTE
# ----------------------------------------------------------
def main():
    """
    Se conecta con el servidor, envía los datos en formato JSON,
    recibe la respuesta y la muestra por pantalla.
    """
    datos = pedir_datos()
    mensaje = json.dumps(datos) + '\n'  # El '\n' marca el final del mensaje

    # Crea el socket TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[+] Conectando al servidor {SERVER_HOST}:{SERVER_PORT} ...")
        s.connect((SERVER_HOST, SERVER_PORT))  # Establece conexión
        print("[+] Conexión establecida. Enviando datos...")

        # Envía el mensaje JSON
        s.sendall(mensaje.encode('utf-8'))

        # Espera la respuesta del servidor
        data = b''
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if b'\n' in data:
                linea, _, _ = data.partition(b'\n')
                try:
                    # Intenta decodificar la respuesta como JSON
                    resp = json.loads(linea.decode('utf-8'))
                    print("\n=== RESPUESTA DEL SERVIDOR ===")
                    print(json.dumps(resp, indent=2, ensure_ascii=False))
                except Exception as e:
                    print("Respuesta no válida:", data.decode('utf-8', errors='replace'))
                break

        print("\n[-] Conexión cerrada.")

# ----------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ----------------------------------------------------------
if __name__ == "__main__":
    main()
