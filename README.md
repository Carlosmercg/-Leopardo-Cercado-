# 🐆 LEOPARDO-CERCADO

**Leopardo-Cercado** es un juego por consola en **Python 3**, basado en un tablero de ajedrez **10x10**.  
El jugador puede elegir controlar al **leopardo** o a las **vacas**, mientras el otro bando es manejado por una **Inteligencia Artificial (IA)**.  
El objetivo del **leopardo** es llegar a la fila opuesta; el de las **vacas** es **bloquearlo estratégicamente**.

---

## 🎮 ¿CÓMO JUGAR?

Al ejecutar el juego, se te preguntará qué bando deseas controlar:

### 1. LEOPARDO
- Ganas si llegas a la última fila (**abajo**).
- Puedes moverte en **diagonales** de **1 o 2 casillas vacías**.

### 2. VACAS
- Ganas si logras **acorralar al leopardo** y evitar que se mueva.
- Te mueves **1 casilla en diagonal hacia adelante (arriba)**.

---

## ⌨️ CONTROLES

- El juego es **por turnos**.
- En cada turno podrás **seleccionar piezas y movimientos válidos** a través del teclado.
- El juego se visualiza en la terminal con **colores ANSI**:

  - **Casillas** negras y blancas alternadas.
  - `L` (rojo): Leopardo  
  - `V` (blanco): Vaca

---

## 🤖 INTELIGENCIA ARTIFICIAL

### IA DE LAS VACAS:
- Analiza múltiples factores:
  - **Reducir la movilidad del leopardo**.
  - **Acercarse a él**.
  - **Evitar los bordes**, que son estratégicamente débiles.

### IA DEL LEOPARDO:
- Intenta **avanzar hacia su objetivo**.
- Selecciona **movimientos de 1 o 2 casillas en diagonal**.

---

## 🧠 LÓGICA DEL JUEGO

- El **tablero es 10x10**.
- Las **vacas** inician en **todas las casillas negras** de la fila inferior.
- El **leopardo** comienza en una **casilla negra aleatoria**.
- **Solo se puede mover sobre casillas negras.**

### EL JUEGO TERMINA CUANDO:
- El leopardo **llega a la fila inferior** → 🏆 **Gana el leopardo**.
- El leopardo **no puede moverse** → 🐄 **Ganan las vacas**.
- Las vacas **no pueden moverse** → 🏆 **Gana el leopardo**.
- El jugador se **rinde manualmente**.

---

## ⚙️ REQUISITOS

- **Python 3.7** o superior  
- **No se requiere instalación de librerías externas**

---

## 🚀 EJECUCIÓN

```bash
python3 juego.py
