import sys
import os
import math
import json

# Intentamos cargar la lógica de control
try:
    from torcs_jm_par import Client, calculate_throttle, apply_brakes, shift_gears, traction_control
except ImportError:
    print("ERROR: No se encuentra torcs_jm_par.py en la carpeta.")
    input("Presiona Enter para salir...")
    sys.exit()

class GADriver(Client):
    def __init__(self, port, individual_id, individual_data):
        # Conexión al puerto específico asignado por el launcher
        super().__init__(p=port)
        self.id = individual_id
        self.trajectory = individual_data
        self.last_idx = 0

    def get_target_pos(self, current_dist):
        """Busca el objetivo de posición en el ADN según la distancia actual."""
        for i in range(self.last_idx, len(self.trajectory)):
            if self.trajectory[i]['dist'] >= current_dist:
                self.last_idx = i
                return self.trajectory[i]['targetPos']
        return 0

    def drive(self):
        S, R = self.S.d, self.R.d
        if not S: return

        # 1. Obtener posición objetivo del Algoritmo Genético
        target_pos = self.get_target_pos(S['distFromStart'])
        
        # 2. Control de dirección (Steering) para seguir el targetPos
        error = S['trackPos'] - target_pos
        steer = (S['angle'] * 10 / math.pi) - (error * 0.25)
        R['steer'] = max(-1, min(1, steer))

        # 3. Control de velocidad y marchas (Tu lógica original)
        R['accel'] = calculate_throttle(S, R)
        R['brake'] = apply_brakes(S)
        R['accel'] = traction_control(S, R['accel'])
        R['gear'] = shift_gears(S)

if __name__ == "__main__":
    try:
        # Argumentos: puerto, id_individuo
        puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0

        print(f"=== COCHE {idx} INICIADO ===")
        
        if not os.path.exists('current_population.json'):
            raise FileNotFoundError("No se encuentra current_population.json")

        with open('current_population.json', 'r') as f:
            poblacion = json.load(f)
        
        # Iniciar cliente
        print(f"Conectando al puerto {puerto}...")
        C = GADriver(puerto, idx, poblacion[idx])
        
        # Bucle de conexión inicial
        connected = False
        while True:
            C.get_servers_input()
            if C.S.d and not connected:
                print(f"¡CONECTADO! Recibiendo telemetría en puerto {puerto}")
                connected = True
            
            if connected:
                C.drive()
                C.respond_to_server()
            
    except Exception as e:
        print(f"\n[ERROR EN COCHE {idx}]: {e}")
        import traceback
        traceback.print_exc()
        input("\nLa ventana se mantiene abierta para leer el error. Enter para cerrar...")