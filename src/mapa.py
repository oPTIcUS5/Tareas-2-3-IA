"""
Mapa de la demostracion: S=inicio, G=meta, #=obstaculo, .=libre.
"""

from dataclasses import dataclass

Posicion = tuple[int, int]  # (fila, columna), empezando desde cero

MAPA_EJEMPLO = (
    "############################",
    "#S......#............#....G#",
    "#.......#............#.....#",
    "#.......#......#.....#.....#",
    "#.......#......#...........#",
    "#.......########.....#.....#",
    "#..............#.....#.....#",
    "#.......#......#.....#####.#",
    "#.......#......#.....#.....#",
    "#.#######......#.....#.....#",
    "#.......#......#######.....#",
    "#.......#......#.....#.....#",
    "#.......#............#.....#",
    "#.......#......#.....#.....#",
    "#..............#...........#",
    "#..............#...........#",
    "############################",
)


@dataclass(frozen=True)
class Mapa:
    celdas: tuple[str, ...]
    inicio: Posicion
    meta: Posicion

    @property
    def filas(self) -> int:
        return len(self.celdas)

    @property
    def columnas(self) -> int:
        return len(self.celdas[0])

    def es_transitable(self, posicion: Posicion) -> bool:
        fila, columna = posicion
        return (
            0 <= fila < self.filas
            and 0 <= columna < self.columnas
            and self.celdas[fila][columna] != "#"
        )

    def vecinos(self, posicion: Posicion) -> list[Posicion]:
        fila, columna = posicion
        # Orden fijo: arriba, abajo, izquierda, derecha.
        candidatos = (
            (fila - 1, columna),
            (fila + 1, columna),
            (fila, columna - 1),
            (fila, columna + 1),
        )
        return [p for p in candidatos if self.es_transitable(p)]


def crear_mapa(celdas: tuple[str, ...] = MAPA_EJEMPLO) -> Mapa:
    """
    Valida un mapa rectangular y encuentra su inicio y meta.
    """
    
    if not celdas or not celdas[0] or any(len(f) != len(celdas[0]) for f in celdas):
        raise ValueError("El mapa debe ser rectangular y no estar vacio.")
    if any(caracter not in "#SG." for fila in celdas for caracter in fila):
        raise ValueError("El mapa solo admite los caracteres #, S, G y .")

    inicios = [(r, c) for r, fila in enumerate(celdas) for c, char in enumerate(fila) if char == "S"]
    metas = [(r, c) for r, fila in enumerate(celdas) for c, char in enumerate(fila) if char == "G"]
    if len(inicios) != 1 or len(metas) != 1:
        raise ValueError("El mapa debe contener exactamente una S y una G.")
    return Mapa(celdas=celdas, inicio=inicios[0], meta=metas[0])
