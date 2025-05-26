import multiprocessing
import random
import time
import os

# Códigos ANSI para colores
RESET = "\033[0m"
FONDO_BLANCO = "\033[47m"
FONDO_NEGRO = "\033[100m"
VACAS = "\033[97mV"     # Letra blanca para vacas
LEOPARDO = "\033[91mL"  # Letra roja para leopardo

TAM = 10  # Tamaño del tablero

def seleccionar_personaje():
    """
    Pregunta al usuario si quiere jugar como Leopardo o Vacas.
    Devuelve un string con el personaje elegido.
    """
    print("=== JUEGO: LEOPARDO vs VACAS ===")
    print("¿Con qué personaje deseas jugar?")
    print("1. Leopardo")
    print("2. Vacas")
    eleccion = ""
    while eleccion not in ["1", "2"]:
        eleccion = input("Selecciona 1 o 2: ")
    return "leopardo" if eleccion == "1" else "vacas"

def es_casilla_negra(x, y):
    """
    Devuelve True si la casilla (x, y) es negra.
    """
    return (x + y) % 2 == 1

def crear_tablero():
    """
    Crea un tablero de tamaño TAM x TAM e inicializa vacas en todas las casillas negras
    de la última fila automáticamente.
    """
    tablero = [["." for _ in range(TAM)] for _ in range(TAM)]
    ultima_fila = TAM - 1
    for col in range(TAM):
        if es_casilla_negra(ultima_fila, col):
            tablero[ultima_fila][col] = "V"
    return tablero


def colocar_leopardo(tablero):
    """
    Coloca el leopardo aleatoriamente en una casilla negra vacía.
    Devuelve su posición como (fila, columna).
    """
    casillas_negras = [(fila, col) for fila in range(TAM) for col in range(TAM)
                       if es_casilla_negra(fila, col) and tablero[fila][col] == "."]
    fila, col = random.choice(casillas_negras)
    tablero[fila][col] = "L"
    return fila, col

def imprimir_tablero(tablero):
    """
    Imprime el tablero en consola con colores ANSI.
    """
    print("    " + "  ".join([str(c) for c in range(TAM)]))
    for f in range(TAM):
        fila_str = f"{f} |"
        for c in range(TAM):
            casilla = tablero[f][c]
            fondo = FONDO_NEGRO if es_casilla_negra(f, c) else FONDO_BLANCO
            if casilla == "V":
                ficha = VACAS
            elif casilla == "L":
                ficha = LEOPARDO
            else:
                ficha = " "
            fila_str += f"{fondo} {ficha} {RESET}"
        print(fila_str)
    print()

# Subproceso que controla las vacas cuando están en modo IA
def proceso_vacas(pipe):
    """
    Proceso hijo que maneja las vacas controladas por IA.
    Evalúa posibles movimientos para minimizar la movilidad del leopardo.
    """
    def posibles_movimientos_leopardo(tablero, pos):
        # Retorna todos los movimientos válidos de 2 pasos del leopardo desde la posición pos
        f, c = pos
        posibles = []
        for df, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            nf, nc = f + df, c + dc
            if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                posibles.append((nf, nc))
        return posibles

    def evaluar_movimiento(tablero, vaca_origen, vaca_destino, pos_leopardo):
        # Simula mover una vaca y evalúa cuántos movimientos le quedan al leopardo
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

            # Buscar posición del leopardo
            pos_leopardo = None
            for f in range(TAM):
                for c in range(TAM):
                    if tablero[f][c] == "L":
                        pos_leopardo = (f, c)
                        break
                if pos_leopardo:
                    break

            mejores_movimientos = []
            menor_movilidad = float('inf')

            for f in range(TAM):
                for c in range(TAM):
                    if tablero[f][c] == "V":
                        for df, dc in [(-1, -1), (-1, 1)]:
                            nf, nc = f + df, c + dc
                            if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                                movilidad = evaluar_movimiento(tablero, (f, c), (nf, nc), pos_leopardo)

                                # Heurística adicional: más cerca del leopardo = mejor
                                distancia = abs(nf - pos_leopardo[0]) + abs(nc - pos_leopardo[1])
                                borde_penalidad = 1 if nc == 0 or nc == TAM - 1 else 0  # Penalizar extremos

                                score = movilidad + distancia * 0.3 + borde_penalidad

                                if score < menor_movilidad:
                                    menor_movilidad = score
                                    mejores_movimientos = [{"type": "move", "from": (f, c), "to": (nf, nc)}]
                                elif score == menor_movilidad:
                                    mejores_movimientos.append({"type": "move", "from": (f, c), "to": (nf, nc)})

            # Elegir aleatoriamente entre los mejores
            if mejores_movimientos:
                pipe.send(random.choice(mejores_movimientos))
            else:
                pipe.send({"type": "pass"})



def mover_pieza(tablero, origen, destino):
    """
    Mueve una pieza del tablero desde origen hasta destino.
    """
    f1, c1 = origen
    f2, c2 = destino
    tablero[f2][c2] = tablero[f1][c1]
    tablero[f1][c1] = "."

def obtener_movimientos_leopardo(tablero, pos, pasos=2):
    """
    Retorna una lista de movimientos válidos para el leopardo desde pos,
    según la cantidad de pasos (1 o 2) en diagonal.
    """
    f, c = pos
    posibles = []
    if pasos == 2:
        desplazamientos = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for df, dc in desplazamientos:
            nf, nc = f + df, c + dc
            midf, midc = f + df // 2, c + dc // 2
            if (0 <= nf < TAM and 0 <= nc < TAM and 0 <= midf < TAM and 0 <= midc < TAM and
                tablero[midf][midc] == "." and tablero[nf][nc] == "."):
                posibles.append((nf, nc))
    elif pasos == 1:
        desplazamientos = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for df, dc in desplazamientos:
            nf, nc = f + df, c + dc
            if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
                posibles.append((nf, nc))
    return posibles

def mover_leopardo_ia(tablero):
    """
    IA para mover al leopardo. Intenta acercarse a la fila TAM-1 (meta).
    """
    for f in range(TAM):
        for c in range(TAM):
            if tablero[f][c] == "L":
                pos = (f, c)
                break

    # Combina movimientos de 1 y 2 pasos y elige el más avanzado
    movimientos = obtener_movimientos_leopardo(tablero, pos, pasos=1) + obtener_movimientos_leopardo(tablero, pos, pasos=2)
    if not movimientos:
        return None  # Leopardo bloqueado

    mejor = max(movimientos, key=lambda x: x[0])  # Elegir el que más avance
    mover_pieza(tablero, pos, mejor)
    return mejor

def obtener_movimientos_vaca(tablero, pos):
    """
    Devuelve todos los movimientos válidos en diagonal hacia adelante para una vaca.
    """
    f, c = pos
    movimientos = []
    for df, dc in [(-1, -1), (-1, 1)]:
        nf, nc = f + df, c + dc
        if 0 <= nf < TAM and 0 <= nc < TAM and tablero[nf][nc] == ".":
            movimientos.append((nf, nc))
    return movimientos

def juego_principal():
    """
    Lógica principal del juego. Alterna turnos entre jugador y IA según personaje elegido.
    """
    personaje = seleccionar_personaje()
    tablero = crear_tablero()
    pos_leopardo = colocar_leopardo(tablero)

    # Crear proceso hijo para IA de vacas
    parent_conn, child_conn = multiprocessing.Pipe()
    proceso = multiprocessing.Process(target=proceso_vacas, args=(child_conn,))
    proceso.start()

    turno = 0
    try:
        while True:
            imprimir_tablero(tablero)

            # Turno del jugador que controla el leopardo
            if personaje == "leopardo" and turno % 2 == 0:
                print("Turno del leopardo (jugador)")
                print(f"El leopardo está en la casilla: {pos_leopardo}")
                pasos = input("¿Deseas mover 1 o 2 casillas diagonalmente? (1/2): ")
                while pasos not in ["1", "2"]:
                    pasos = input("Selecciona 1 o 2: ")
                movimientos = obtener_movimientos_leopardo(tablero, pos_leopardo, int(pasos))
                if not movimientos:
                    imprimir_tablero(tablero)
                    print("¡Las vacas ganan! El leopardo está acorralado.")
                    break

                # Mostrar y elegir movimiento
                for i, mov in enumerate(movimientos, 1):
                    print(f"{i}: Mover a {mov}")
                eleccion = input(f"Elige (1-{len(movimientos)}): ")
                while not eleccion.isdigit() or int(eleccion) not in range(1, len(movimientos)+1):
                    eleccion = input("Entrada inválida. Elige de nuevo: ")

                destino = movimientos[int(eleccion)-1]
                mover_pieza(tablero, pos_leopardo, destino)
                pos_leopardo = destino

                if pos_leopardo[0] == TAM - 1:
                    imprimir_tablero(tablero)
                    print("¡El leopardo gana!")
                    break

            # Turno del jugador que controla las vacas
            elif personaje == "vacas" and turno % 2 == 1:
                print("Turno de las vacas (jugador)")
                vacas_disponibles = [(f, c) for f in range(TAM) for c in range(TAM) if tablero[f][c] == "V"]

                if not any(obtener_movimientos_vaca(tablero, vaca) for vaca in vacas_disponibles):
                    imprimir_tablero(tablero)
                    print("¡El leopardo gana! Las vacas están bloqueadas.")
                    break

                # Elegir vaca y movimiento
                while True:
                    for i, vaca in enumerate(vacas_disponibles, 1):
                        print(f"{i}: {vaca}")
                    eleccion_vaca = input(f"Elige una vaca (1-{len(vacas_disponibles)}) o 'q' para rendirse: ")
                    if eleccion_vaca.lower() == "q":
                        print("Te rendiste. ¡El leopardo gana!")
                        return
                    if not eleccion_vaca.isdigit() or not (1 <= int(eleccion_vaca) <= len(vacas_disponibles)):
                        print("Opción inválida.")
                        continue

                    vaca_sel = vacas_disponibles[int(eleccion_vaca) - 1]
                    movimientos = obtener_movimientos_vaca(tablero, vaca_sel)

                    if not movimientos:
                        print(f"La vaca en {vaca_sel} no tiene movimientos válidos.")
                        continue

                    for i, mov in enumerate(movimientos, 1):
                        print(f"{i}: {vaca_sel} -> {mov}")
                    print("0: Volver a elegir vaca")
                    eleccion_mov = input(f"Elige un movimiento (1-{len(movimientos)}) o 0 para volver: ")
                    if eleccion_mov == "0":
                        continue
                    if not eleccion_mov.isdigit() or not (1 <= int(eleccion_mov) <= len(movimientos)):
                        print("Opción inválida.")
                        continue

                    destino = movimientos[int(eleccion_mov) - 1]
                    mover_pieza(tablero, vaca_sel, destino)
                    break

            else:
                # Turno de la IA (leopardo o vacas)
                if personaje == "leopardo":
                    print("Turno de las vacas (IA)")
                    parent_conn.send({"type": "state", "board": tablero})
                    respuesta = parent_conn.recv()
                    if respuesta["type"] == "move":
                        mover_pieza(tablero, respuesta["from"], respuesta["to"])
                    else:
                        imprimir_tablero(tablero)
                        print("Las vacas no pueden mover. ¡El leopardo gana!")
                        break
                else:
                    print("Turno del leopardo (IA)")
                    pos = mover_leopardo_ia(tablero)
                    if pos is None:
                        imprimir_tablero(tablero)
                        print("¡Las vacas ganan! El leopardo está acorralado.")
                        break
                    elif pos[0] == TAM - 1:
                        imprimir_tablero(tablero)
                        print("¡El leopardo gana!")
                        break

            turno += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nEl jugador se rindió. ¡El oponente gana automáticamente!")
    finally:
        proceso.terminate()

def limpiar_consola():
    """
    Limpia la consola dependiendo del sistema operativo.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

# Punto de entrada principal
if __name__ == "__main__":
    while True:
        limpiar_consola()
        juego_principal()
        print("\n¿Quieres jugar otra vez?")
        print("1. Sí")
        print("2. No, salir")
        opcion = ""
        while opcion not in ["1", "2"]:
            opcion = input("Selecciona 1 o 2: ")
        if opcion == "2":
            print("¡Gracias por jugar!")
            break
