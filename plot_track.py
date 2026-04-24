import json
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_track_and_elevation(file_path):
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ordenamos por distancia para que las gráficas sean fluidas
    data = sorted(data, key=lambda x: x['distFromStart'])

    # Listas para la vista 2D (Top-down)
    cx, cy = [0], [0]
    lx, ly = [], []
    rx, ry = [], []
    angle_acumulado = 0

    # Listas para el perfil de altura
    distancias = []
    alturas_z = []
    pendientes = []

    for i in range(1, len(data)):
        p = data[i]
        prev = data[i-1]
        
        # --- 1. GEOMETRÍA TOP-DOWN ---
        step = p['distFromStart'] - prev['distFromStart']
        if step < 0: continue # Ignorar saltos de meta
        
        angle_acumulado += (p['angle'] - prev['angle'])
        
        nx = cx[-1] + step * np.cos(angle_acumulado)
        ny = cy[-1] + step * np.sin(angle_acumulado)
        cx.append(nx)
        cy.append(ny)
        
        perp = angle_acumulado + np.pi/2
        lx.append(nx + p['track'][18] * np.cos(perp))
        ly.append(ny + p['track'][18] * np.sin(perp))
        rx.append(nx - p['track'][0] * np.cos(perp))
        ry.append(ny - p['track'][0] * np.sin(perp))

        # --- 2. DATOS DE ELEVACIÓN ---
        distancias.append(p['distFromStart'])
        alturas_z.append(p['z'])
        pendientes.append(p['pitch_calc'])

    # --- CREAR LOS GRÁFICOS ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14), gridspec_kw={'height_ratios': [2, 1]})

    # SUBGRÁFICO 1: VISTA DESDE ARRIBA (TOP-DOWN)
    ax1.fill(np.append(lx, rx[::-1]), np.append(ly, ry[::-1]), color='gray', alpha=0.3)
    ax1.plot(lx, ly, 'k-', linewidth=1, alpha=0.5)
    ax1.plot(rx, ry, 'k-', linewidth=1, alpha=0.5)
    ax1.plot(cx, cy, 'r--', linewidth=0.8, label='Línea de Carrera')
    
    # Marcar el Corkscrew (aprox metros 2500-2600 en Laguna Seca)
    ax1.set_title("Vista Aérea del Circuito (Top-Down)")
    ax1.axis('equal')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # SUBGRÁFICO 2: PERFIL DE ELEVACIÓN (DESNIVEL)
    ax2.fill_between(distancias, alturas_z, min(alturas_z)-1, color='brown', alpha=0.2)
    ax2.plot(distancias, alturas_z, color='brown', linewidth=2, label='Altura (Z)')
    
    # Añadir una línea para la pendiente (pitch)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(distancias, pendientes, color='blue', alpha=0.3, label='Pendiente (Rad)')
    ax2_twin.set_ylabel("Inclinación (Radianes)", color='blue')

    ax2.set_title("Perfil de Desnivel (Corkscrew)")
    ax2.set_xlabel("Distancia Recorrida (Metros)")
    ax2.set_ylabel("Altura sobre el nivel de pista (Z)")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    print("Mostrando visualización completa...")
    plt.show()

if __name__ == "__main__":
    plot_track_and_elevation('track_data.json')