import json
import random
import os

def generate_initial_population(file_path, pop_size=10):
    with open(file_path, 'r') as f:
        reference_data = json.load(f)
    
    population = []
    
    for i in range(pop_size):
        # Creamos un individuo basado en tu mapeo pero con pequeñas mutaciones
        individual = []
        for point in reference_data:
            # Mutación: movemos el trackPos original un poco a la izquierda o derecha
            # El valor de trackPos debe estar entre -1 y 1
            mutation = random.uniform(-0.15, 0.15) 
            new_pos = max(-0.95, min(0.95, point['trackPos'] + mutation))
            
            individual.append({
                'dist': point['distFromStart'],
                'targetPos': new_pos
            })
        
        population.append(individual)
    
    # Guardamos la población para que el driver la use
    with open('current_population.json', 'w') as f:
        json.dump(population, f)
    
    print(f"Generación 0 creada con {pop_size} individuos.")

if __name__ == "__main__":
    generate_initial_population('track_data.json')