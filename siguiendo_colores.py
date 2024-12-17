#
# PROYECTO OpenCV - SEGUIMIENTO DE COLORES
# Autor: Juan Pablo Márquez
#

import cv2
import numpy as np
import time
import random

cap = cv2.VideoCapture(0)

# Rango de color
color_lower = np.array([0, 0, 0])
color_upper = np.array([0, 0, 0])

# Flag de si se encuentra un color seleccionado
color_selected = False

# Coordenadas de la zona de puntuación
frame_width, frame_height = 640, 480
score_zone_center = (random.randint(50, frame_width - 50), random.randint(50, frame_height - 50))
score_zone_radius = 50

# Puntuación y temporizador
score = 0
start_time = None
game_duration = 20  # DURACIÓN DEL JUEGO (segundos)
game_active = False

# Función para seleccionar el color
def select_color(event, x, y, flags, param):
    global color_lower, color_upper, color_selected, start_time, score, game_active
    if event == cv2.EVENT_LBUTTONDOWN:
        if 500 <= x <= 640 and 10 <= y <= 50:
            # Si el clic está dentro del botón de "Finalizar Partida"
            end_game()
        else:
            # Se selecciona el color en la posición del clic
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)  # Corregir efecto espejo
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            selected_color = hsv_frame[y, x]
            
            # Establecer un rango de color alrededor del color seleccionado
            sensitivity = 20
            color_lower = np.array([max(0, selected_color[0] - sensitivity), 100, 100])
            color_upper = np.array([min(179, selected_color[0] + sensitivity), 255, 255])
            color_selected = True
            
            # Reiniciar puntuación y temporizador
            score = 0
            start_time = time.time()
            game_active = True
            print("Color seleccionado: HSV =", selected_color)

# Finalizar el juego y mostrar la pantalla de resumen
def end_game():
    global game_active
    game_active = False
    end_time = time.time()
    total_time = int(end_time - start_time) if start_time else 0
    
    # Se muestra la pantalla de resumen
    summary = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    cv2.putText(summary, "Resumen de Partida", (frame_width//4, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(summary, f"Puntuacion final: {score}", (frame_width//4, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(summary, f"Tiempo total: {total_time}s", (frame_width//4, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 1, cv2.LINE_AA)
    cv2.imshow("Resumen", summary)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    exit()


cv2.namedWindow("Siguiendo colores")
cv2.setMouseCallback("Siguiendo colores", select_color)

# Detectar el objeto del color seleccionado
def detect_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            return (int(x), int(y))
    
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Corregir efecto espejo -> MUY IMPORTANTE
    frame = cv2.flip(frame, 1)

    # Solo se detecta el objeto solo si el color ya fue seleccionado y el juego está activo
    if color_selected and game_active:
        object_center = detect_object(frame)
    else:
        object_center = None
    
    # Zona de puntuación (círculo azul)
    cv2.circle(frame, score_zone_center, score_zone_radius, (255, 0, 0), 2)
    
    # Se comprueba si el objeto está en la zona de puntuación
    if object_center:
        dist = np.sqrt((object_center[0] - score_zone_center[0])**2 + (object_center[1] - score_zone_center[1])**2)
        if dist < score_zone_radius:
            score += 1
            cv2.putText(frame, "Punto!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Se mueve la zona de puntuación a una nueva posición aleatoria
            score_zone_center = (random.randint(50, frame_width - 50), random.randint(50, frame_height - 50))

    # Tiempo restante
    if start_time is not None:
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, game_duration - elapsed_time)
    else:
        remaining_time = game_duration

    # Recuadros de puntuación y tiempo
    cv2.rectangle(frame, (10, 10), (140, 50), (0, 0, 0), -1)  # PUNTUACIÓN
    cv2.putText(frame, f"Puntuacion: {score}", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.rectangle(frame, (150, 10), (280, 50), (0, 0, 0), -1)  # TIEMPO
    cv2.putText(frame, f"Tiempo: {remaining_time}s", (155, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Botón de "Finalizar Partida" y detectar clic sobre él
    cv2.rectangle(frame, (500, 10), (640, 50), (0, 0, 255), -1)
    cv2.putText(frame, "Finalizar", (510, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Si el tiempo se acaba el juego finaliza
    if remaining_time <= 0 and game_active:
        end_game()
        break
    
    cv2.imshow("Siguiendo colores", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
