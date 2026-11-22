"""
A* con historial de expansion y BFS para comparar en el mismo mapa.
"""


from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count

from .mapa import Mapa, Posicion


def manhattan(actual: Posicion, meta: Posicion) -> int:
    """
    Estimacion admisible para una cuadricula de cuatro direcciones y costo 1.
    """
    
    return abs(actual[0] - meta[0]) + abs(actual[1] - meta[1])


@dataclass(frozen=True)
class Paso:
    """
    Fotografia del algoritmo justo despues de expandir un nodo.
    """
    
    actual: Posicion
    g: int
    h: int
    f: int
    frontera: frozenset[Posicion]
    explorados: frozenset[Posicion]
    orden_expansion: tuple[Posicion, ...]


@dataclass(frozen=True)
class Resultado:
    ruta: tuple[Posicion, ...]
    costo: int | None
    explorados: int
    pasos: tuple[Paso, ...] = ()


def reconstruir_ruta(padres: dict[Posicion, Posicion], inicio: Posicion, meta: Posicion) -> tuple[Posicion, ...]:
    ruta = [meta]
    actual = meta
    while actual != inicio:
        actual = padres[actual]
        ruta.append(actual)
    ruta.reverse()
    return tuple(ruta)


def a_estrella(mapa: Mapa) -> Resultado:
    """
    Expande el menor f=g+h. Entre empates, prefiere el menor h.
    """
    
    inicio, meta = mapa.inicio, mapa.meta
    desempate = count()
    h_inicial = manhattan(inicio, meta)
    
    # Tuplas de prioridad: (f, h, numero_de_insercion, posicion).
    cola: list[tuple[int, int, int, Posicion]] = []
    heappush(cola, (h_inicial, h_inicial, next(desempate), inicio))

    g: dict[Posicion, int] = {inicio: 0}
    padres: dict[Posicion, Posicion] = {}
    cerrados: set[Posicion] = set()
    orden: list[Posicion] = []
    pasos: list[Paso] = []

    while cola:
        _, _, _, actual = heappop(cola)
        if actual in cerrados:  # Ignora entradas antiguas de la cola.
            continue

        cerrados.add(actual)
        orden.append(actual)
        g_actual = g[actual]
        h_actual = manhattan(actual, meta)

        if actual != meta:
            for vecino in mapa.vecinos(actual):
                if vecino in cerrados:
                    continue
                nuevo_g = g_actual + 1  # Todos los movimientos cuestan uno.
                if nuevo_g < g.get(vecino, float("inf")):
                    g[vecino] = nuevo_g
                    padres[vecino] = actual
                    h_vecino = manhattan(vecino, meta)
                    heappush(
                        cola,
                        (nuevo_g + h_vecino, h_vecino, next(desempate), vecino),
                    )

        # La frontera son los nodos descubiertos pero todavia no expandidos.
        frontera = frozenset(g.keys() - cerrados)
        pasos.append(
            Paso(
                actual=actual,
                g=g_actual,
                h=h_actual,
                f=g_actual + h_actual,
                frontera=frontera,
                explorados=frozenset(cerrados),
                orden_expansion=tuple(orden),
            )
        )

        if actual == meta:
            ruta = reconstruir_ruta(padres, inicio, meta)
            return Resultado(ruta, len(ruta) - 1, len(cerrados), tuple(pasos))

    return Resultado((), None, len(cerrados), tuple(pasos))


def bfs(mapa: Mapa) -> Resultado:
    """Busqueda sin heuristica: visita celdas por capas de distancia."""
    cola = deque([mapa.inicio])
    visitados = {mapa.inicio}
    padres: dict[Posicion, Posicion] = {}
    expandidos = 0

    while cola:
        actual = cola.popleft()
        expandidos += 1
        if actual == mapa.meta:
            ruta = reconstruir_ruta(padres, mapa.inicio, mapa.meta)
            return Resultado(ruta, len(ruta) - 1, expandidos)
        for vecino in mapa.vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = actual
                cola.append(vecino)

    return Resultado((), None, expandidos)
