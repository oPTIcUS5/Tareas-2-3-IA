# Tarea 2.3 — Búsqueda A* sobre una cuadrícula

## Descripción

Implementación de A* en Python para encontrar una ruta de costo mínimo entre un punto inicial (S) y una meta (G) en un laberinto con obstáculos (#). La demostración muestra el orden de expansión, la frontera (nodos abiertos), los nodos explorados (cerrados) y el camino final.

Se incluye BFS, una búsqueda no informada, para comparar en el mismo mapa el costo de la ruta y la cantidad de nodos expandidos.

## Requisitos

- Python 3.10 o superior.
- Bibliotecas indicadas en `requirements.txt`.

## Instalación y ejecución

Desde la carpeta raíz del proyecto:

```bash
python -m pip install -r requirements.txt
python main.py
```

En macOS o Linux, el comando de Python también puede ser `python3`.

Para crear imágenes para la entrega:

```bash
python main.py --modo evidencias
```

Para generar un GIF de la expansión y las imágenes:

```bash
python main.py --modo gif
```

Para ver únicamente los cálculos en consola, sin abrir una ventana:

```bash
python main.py --modo consola --detalles
```

Para ajustar la velocidad de la animación (milisegundos por expansión):

```bash
python main.py --intervalo 100
```

**Controles de la ventana:** ESPACIO pausa o reanuda; flecha derecha avanza un paso; flecha izquierda retrocede; R vuelve al inicio.

## Cómo funciona

Se representa cada estado con una coordenada `(fila, columna)`. Los movimientos posibles son arriba, abajo, izquierda y derecha, con costo **1** por movimiento. No se permiten movimientos diagonales ni atravesar obstáculos.

A* mantiene dos conjuntos conceptuales:

- **Frontera o abiertos:** nodos descubiertos pero aún no expandidos.
- **Explorados o cerrados:** nodos que ya se expandieron.

Para priorizar los nodos utiliza:

- `g(n)`: costo conocido desde S hasta `n`.
- `h(n)`: distancia Manhattan desde `n` hasta G.
- `f(n) = g(n) + h(n)`: costo total estimado.

En cada iteración se extrae de una **cola de prioridad** el nodo con menor `f`. Si hay empate, se elige el de menor `h` (y después el que fue insertado primero). Se examinan sus vecinos transitables y se actualizan sus costos cuando se encuentra un recorrido mejor. Al alcanzar la meta, se reconstruye el camino mediante los predecesores guardados.

### ¿Por qué Manhattan es admisible?

Para dos celdas `n = (r, c)` y `G = (rG, cG)`:

`h(n) = |r-rG| + |c-cG|`.

Con movimientos de cuatro direcciones y costo unitario, hacen falta al menos esa cantidad de movimientos para llegar a G. Los obstáculos pueden forzar recorridos más largos, nunca más cortos. Por ello, `h(n)` no sobreestima el costo real y es una heurística admisible. Además, satisface la consistencia entre vecinos, por lo que A* encuentra una ruta óptima con el manejo de nodos cerrados implementado.

### Comparación con BFS

BFS explora por niveles de distancia sin considerar la proximidad estimada a la meta. A* utiliza `h` para orientar su búsqueda. En este laberinto, ambas búsquedas obtienen el mismo costo de ruta, pero A* expande menos celdas. La cantidad exacta se imprime al ejecutar el programa y se ilustra en `evidencias/02_comparacion.png`.

### Resultados de la instancia incluida

El mapa de ejemplo tiene 17 filas y 28 columnas, con inicio `(1, 1)` y meta `(1, 26)`. La distancia Manhattan inicial es **25**, pero por los muros la longitud real del camino más corto es **51** movimientos: un ejemplo concreto de que la heurística puede **subestimar** el costo sin perder admisibilidad.

Al ejecutar el proyecto:

| Métrica | A* | BFS |
|---|---:|---:|
| Costo del camino | 51 | 51 |
| Nodos expandidos | 170 | 247 |

En esta instancia A* expande **31.2 % menos nodos** que BFS.

**Nota:** A* no siempre expande menos nodos que BFS en cualquier mapa o bajo cualquier desempate. La comparación presentada corresponde a esta instancia.

## Visualización

- Blanco: celda libre no descubierta.
- Gris oscuro: obstáculo.
- Naranja: frontera o conjunto abierto.
- Azul: nodo ya explorado o cerrado; su número indica el orden de expansión.
- Morado: nodo expandido en el paso actual.
- Verde claro: ruta óptima al terminar.
- Verde oscuro S: inicio.
- Rojo G: meta.

El panel lateral indica el nodo actual, `g`, `h`, `f`, los tamaños de los conjuntos, los últimos nodos expandidos y el resultado comparativo con BFS.

## Archivos

```
.
├── main.py                   # Ejecuta la demostración
├── src/
│   ├── mapa.py               # Laberinto, posiciones y vecinos
│   ├── busqueda.py           # A*, BFS y registro de pasos
│   └── visualizacion.py      # Animación, PNG y GIF
├── tests/
│   └── test_busqueda.py      # Pruebas unitarias
├── requirements.txt
└── README.md
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Los casos comprueban la validez del camino, su costo óptimo frente a BFS, la admisibilidad de Manhattan en este mapa, los datos del historial y el comportamiento cuando no existe camino.

## Evidencias

Ejecutar `python main.py --modo evidencias` genera:

- `evidencias/01_ruta_final.png`: recorrido final con datos del algoritmo.
- `evidencias/02_comparacion.png`: número de nodos expandidos por A* y BFS.

Ejecutar `python main.py --modo gif` también genera:

- `evidencias/03_busqueda_animada.gif`: evolución visual de la búsqueda.

El GIF muestrea una de cada dos expansiones para reducir su tamaño; la ventana interactiva permite ver todos los pasos.
