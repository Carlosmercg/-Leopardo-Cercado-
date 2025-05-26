# -Leopardo-Cercado-

Leopardo-Cercado es un juego por consola en Python 3, basado en un tablero de ajedrez 10x10. El jugador puede elegir controlar al leopardo o a las vacas, mientras el otro bando es manejado por una inteligencia artificial (IA). El objetivo del leopardo es llegar a la fila opuesta; el de las vacas es bloquearlo estratégicamente.

🎮 ¿Cómo jugar?
Al ejecutar el juego, se te preguntará qué bando deseas controlar:

1. Leopardo: Ganas si llegas a la última fila (abajo). Puedes moverte en diagonales de 1 o 2 casillas vacías.

2. Vacas: Ganas si logras acorralar al leopardo y evitar que se mueva. Te mueves solo 1 casilla en diagonal hacia adelante (arriba).

Controles
El juego es por turnos.

En cada turno podrás seleccionar piezas y movimientos válidos a través del teclado.

El juego se visualiza en la terminal con colores ANSI:

Casillas negras y blancas alternadas.

L (rojo): Leopardo

V (blanco): Vaca

🤖 Inteligencia Artificial
La IA de las vacas analiza múltiples factores:

Reducir la movilidad del leopardo.

Acercarse a él.

Evitar los bordes, que son estratégicamente débiles.

La IA del leopardo intenta avanzar lo más posible hacia su objetivo, seleccionando movimientos de 1 o 2 casillas en diagonal.

🧠 Lógica del juego
El tablero es de tamaño 10x10, y las vacas inician en todas las casillas negras de la fila inferior.

El leopardo comienza en una casilla negra aleatoria.

Solo se puede mover sobre casillas negras.

El juego termina cuando:

El leopardo llega a la fila inferior → Gana el leopardo.

El leopardo no puede moverse → Ganan las vacas.

Las vacas no pueden moverse → Gana el leopardo.

El jugador se rinde manualmente.

⚙️ Requisitos
Python 3.7 o superior

No se requiere instalación de librerías externas

🚀 Ejecución
python3 juego.py