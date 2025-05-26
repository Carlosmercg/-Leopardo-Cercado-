import multiprocessing
import random
import time

TAM = 8

def es_casilla_negra(x, y):
    return (x + y) % 2 == 1

def crear_tablero():
    tablero = [["." for _ in range(TAM)] for _ in range(TAM)]
    # Vacas en la fila 7 (última fila), en casillas negras
    for col in range(TAM):
        if es_casilla_negra(7, col):
            tablero[7][col] = "V"
    return tablero

def colocar_leopardo(tablero):
    casillas_negras = [(fila, col) for fila in range(TAM) for col in range(TAM)
                       if es_casilla_negra(fila, col) and tablero[fila][col] == "."]
    fila, col = random.choice(casillas_negras)
    tablero[fila][col] = "L"
    return fila, col

def imprimir_tablero(tablero):
    for fila in tablero:
        print(" ".join(fila))
    print()

# Subproceso para vacas
def proceso_vacas(pipe):
    def posibles_movimientos_leopardo(tablero, pos):
        f, c = pos
        posibles = []
        for df, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            nf, nc = f + df, c + dc
            if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                posibles.append((nf, nc))
        return posibles

    def evaluar_movimiento(tablero, vaca_origen, vaca_destino, pos_leopardo):
        # Simular el tablero
        f1, c1 = vaca_origen
        f2, c2 = vaca_destino
        copia = [fila[:] for fila in tablero]
        copia[f2][c2] = "V"
        copia[f1][c1] = "."
        return len(posibles_movimientos_leopardo(copia, pos_leopardo))

    while True:
        mensaje = pipe.recv()
        if mensaje["type"] == "state":
            tablero = mensaje["board"]
            pos_leopardo = None
            for f in range(TAM):
                for c in range(TAM):
                    if tablero[f][c] == "L":
                        pos_leopardo = (f, c)
                        break
                if pos_leopardo:
                    break

            mejor_mov = None
            menor_movilidad = float('inf')

            for f in range(TAM):
                for c in range(TAM):
                    if tablero[f][c] == "V":
                        for df, dc in [(-1, -1), (-1, 1)]:
                            nf, nc = f + df, c + dc
                            if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                                movilidad = evaluar_movimiento(tablero, (f, c), (nf, nc), pos_leopardo)
                                if movilidad < menor_movilidad:
                                    menor_movilidad = movilidad
                                    mejor_mov = {"type": "move", "from": (f, c), "to": (nf, nc)}

            if mejor_mov:
                pipe.send(mejor_mov)
            else:
                pipe.send({"type": "pass"})


# Movimiento del leopardo (por ahora fijo o aleatorio entre válidos)
def obtener_movimientos_leopardo(tablero, pos):
    f, c = pos
    posibles = []
    for df, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        nf, nc = f + df, c + dc
        if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
            posibles.append((nf, nc))
    return posibles

def mover_pieza(tablero, origen, destino):
    f1, c1 = origen
    f2, c2 = destino
    tablero[f2][c2] = tablero[f1][c1]
    tablero[f1][c1] = "."

# Juego principal
def juego_principal():
    tablero = crear_tablero()
    pos_leopardo = colocar_leopardo(tablero)

    parent_conn, child_conn = multiprocessing.Pipe()
    proceso = multiprocessing.Process(target=proceso_vacas, args=(child_conn,))
    proceso.start()

    turno = 0
    try:
        while True:
            imprimir_tablero(tablero)
            if turno % 2 == 0:
                print("Turno del leopardo")
                print(f"El leopardo está en la casilla: {pos_leopardo}")
                movimientos = obtener_movimientos_leopardo(tablero, pos_leopardo)
                if not movimientos:
                    print("¡Las vacas ganan! El leopardo está acorralado.")
                    break

                opciones = {
                    "1": (-2, -2),  # ↖
                    "2": (-2, 2),   # ↗
                    "3": (2, -2),   # ↙
                    "4": (2, 2)     # ↘
                }

                print("Opciones de movimiento:")
                for key, (df, dc) in opciones.items():
                    nf, nc = pos_leopardo[0] + df, pos_leopardo[1] + dc
                    if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                        print(f"{key}: mover a ({nf}, {nc})")

                opcion_valida = False
                while not opcion_valida:
                    eleccion = input("Elige una opción (1-4): ")
                    if eleccion in opciones:
                        df, dc = opciones[eleccion]
                        nf, nc = pos_leopardo[0] + df, pos_leopardo[1] + dc
                        if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                            mover_pieza(tablero, pos_leopardo, (nf, nc))
                            pos_leopardo = (nf, nc)
                            opcion_valida = True
                        else:
                            print("Movimiento inválido. Casilla ocupada o fuera de rango.")
                    else:
                        print("Opción no válida. Intenta de nuevo.")

                if pos_leopardo[0] == 7:
                    print("¡El leopardo gana!")
                    break
            else:
                print("Turno de las vacas")
                parent_conn.send({"type": "state", "board": tablero})
                respuesta = parent_conn.recv()
                if respuesta["type"] == "move":
                    mover_pieza(tablero, respuesta["from"], respuesta["to"])
                else:
                    print("Las vacas no pueden mover.")
            turno += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nEl jugador se rindió. ¡Las vacas ganan automáticamente!")
    finally:
        proceso.terminate()



if __name__ == "__main__":
    juego_principal()
