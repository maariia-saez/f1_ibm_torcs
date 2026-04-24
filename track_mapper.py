import socket
import sys
import math
import json
import os
import time

# --- CONFIGURACIÓN DE RUTAS ---
directorio_script = os.path.dirname(os.path.abspath(__file__))
if directorio_script not in sys.path:
    sys.path.append(directorio_script)

try:
    from torcs_jm_par import Client, calculate_steering, calculate_throttle, apply_brakes, shift_gears, traction_control
    print("Módulo torcs_jm_par cargado.")
except ImportError:
    print("Error: No se encontró torcs_jm_par.py.")
    sys.exit()

def save_data_to_json(file_path, data_list):
    """Guarda los datos y asegura que se escriban físicamente en el disco."""
    print(f"\n[SISTEMA] Escribiendo {len(data_list)} puntos de telemetría...")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=2)
            f.flush()
            os.fsync(f.fileno()) 
        print(f"[OK] Archivo guardado: {file_path} ({os.path.getsize(file_path)} bytes)")
    except Exception as e:
        print(f"[ERROR] Error al guardar: {e}")

if __name__ == "__main__":
    ruta_archivo = os.path.join(directorio_script, 'track_data.json')
    
    # REQUISITO: Borrar y reescribir siempre
    if os.path.exists(ruta_archivo):
        try:
            os.remove(ruta_archivo)
            print(">>> Archivo anterior ELIMINADO. Iniciando nueva captura limpia.")
        except:
            pass

    try:
        C = Client(p=3001)
    except:
        C = Client(p=3001, H="localhost")

    track_data = []
    last_recorded_dist = -999
    prev_dist = 0
    estado = 0 # 0: Esperando Meta, 1: Grabando

    print("\n" + "="*60)
    print("MAPPER LAGUNA SECA - DETECCIÓN DE PENDIENTE")
    print("Esperando cruce de meta para iniciar...")
    print("="*60)

    try:
        while True:
            C.get_servers_input()
            if not C.S.d: break

            S, R = C.S.d, C.R.d
            curr_dist = S.get('distFromStart', 0)

            # --- CONDUCCIÓN ---
            R['steer'] = calculate_steering(S)
            R['accel'] = calculate_throttle(S, R)
            R['brake'] = apply_brakes(S)
            R['accel'] = traction_control(S, R['accel'])
            R['gear'] = shift_gears(S)

            # --- CONTROL DE META ---
            if estado == 0 and (curr_dist < 10 and prev_dist > 3000):
                estado = 1
                print("\n[INICIO] ¡Meta detectada! Capturando verticalidad...")

            # --- GRABACIÓN DE TELEMETRÍA ---
            if estado == 1:
                if abs(curr_dist - last_recorded_dist) > 1.0: # Resolución aumentada a 1.0m
                    
                    # 1. Cálculo de Slip (según tu fórmula)
                    slip_val = max(0, ((S['wheelSpinVel'][2] + S['wheelSpinVel'][3]) - 
                                     (S['wheelSpinVel'][0] + S['wheelSpinVel'][1])))
                    
                    # 2. Cálculo de Inclinación Estimada (Pitch)
                    pitch_estimado = 0
                    if abs(S['speedX']) > 1:
                        pitch_estimado = math.atan2(S['speedZ'], S['speedX'])

                    # 3. Detección Predictiva de Curvas (Feature Engineering)
                    track_sensors = S['track']
                    max_sensor_val = max(track_sensors)
                    max_sensor_idx = track_sensors.index(max_sensor_val)
                    
                    # El sensor central es el índice 9 (0 grados)
                    if max_sensor_idx > 10:
                        curve_direction = 'Right'
                    elif max_sensor_idx < 8:
                        curve_direction = 'Left'
                    else:
                        curve_direction = 'Straight'
                        
                    dist_to_corner = track_sensors[9] # Distancia libre al frente
                    track_width = track_sensors[0] + track_sensors[18] # Estimación cruda del ancho

                    track_data.append({
                        "distFromStart": curr_dist,
                        "trackPos": S['trackPos'],
                        "angle": S['angle'],
                        "z": S.get('z', 0),
                        "speedZ": S.get('speedZ', 0),
                        "pitch_calc": pitch_estimado,
                        "track": track_sensors,
                        "speedX": S['speedX'],
                        "slip": slip_val,
                        "accel": R['accel'],
                        "brake": R['brake'],
                        "steer": R['steer'],
                        # Nuevas métricas predictivas:
                        "curve_direction": curve_direction,
                        "dist_to_corner": dist_to_corner,
                        "track_width": track_width
                    })
                    last_recorded_dist = curr_dist
                
                # Fin de vuelta
                if len(track_data) > 500 and curr_dist < 5:
                    print(f"\n[FIN] Vuelta completada.")
                    break

            prev_dist = curr_dist
            C.respond_to_server()
            
            if int(time.time() * 10) % 5 == 0:
                print(f"[{'GRABANDO' if estado==1 else 'ESPERANDO'}] Puntos: {len(track_data)} | Altura (Z): {S.get('z',0):.2f} | V.Vert: {S.get('speedZ',0):.2f}    ", end="\r")

    except KeyboardInterrupt:
        print("\n\nGrabación interrumpida.")
    finally:
        if len(track_data) > 100:
            save_data_to_json(ruta_archivo, track_data)
        C.shutdown()