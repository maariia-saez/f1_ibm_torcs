import subprocess
import time
import os
import sys

# Configuración de rutas
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_driver = os.path.join(directorio_actual, 'ga_driver.py')
python_exe = sys.executable 

NUM_COCHES = 10 

print("====================================================")
print("   LANZADOR MULTI-COCHE: LAGUNA SECA EVOLUTION")
print("====================================================")
print(f"Directorio: {directorio_actual}")

# Comprobación de archivos
if not os.path.exists(ruta_driver):
    print(f"ERROR: No se encuentra {ruta_driver}")
    sys.exit()

procesos = []

for i in range(NUM_COCHES):
    puerto = 3001 + i
    
    # comando: abre una nueva consola, ejecuta python, el script, puerto e ID
    # 'cmd /k' hace que la ventana NO se cierre si el script termina o falla
    comando = f'start "Coche_{i}_Puerto_{puerto}" cmd /k "{python_exe}" "{ruta_driver}" {puerto} {i}'
    
    print(f" -> Lanzando Individuo {i} en Puerto {puerto}...")
    
    # Ejecutamos el comando
    p = subprocess.Popen(comando, shell=True, cwd=directorio_actual)
    procesos.append(p)
    
    # Esperar un poco entre lanzamientos para no colapsar el socket de TORCS
    time.sleep(0.6)

print("\n[ÉXITO] Los 10 procesos han sido enviados al sistema.")
print("INSTRUCCIONES:")
print("1. Ve a TORCS.")
print("2. Race > Quick Race > Configure Race.")
print("3. Asegúrate de que hay 10 'scr_server' en la lista de pilotos.")
print("4. Dale a 'New Race'.")
print("====================================================")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nLanzador cerrado. Las ventanas de los coches deben cerrarse manualmente.")