"""
Visualiza la frontera, el orden de expansion, g/h/f y la ruta final.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from .busqueda import Resultado
from .mapa import Mapa, Posicion

# 0 libre, 1 muro, 2 explorado, 3 frontera, 4 actual,
# 5 ruta optima, 6 inicio, 7 meta.
COLORES = [
    "#FAFAFA", "#252D3B", "#BED8F5", "#F7BD69",
    "#A88BE6", "#5FD4A1", "#128E76", "#E96E72",
]
CMAP = ListedColormap(COLORES)
NORM = BoundaryNorm(np.arange(-0.5, 8.5, 1), CMAP.N)
LEYENDA = [
    Patch(facecolor=COLORES[1], label="Obstaculo"),
    Patch(facecolor=COLORES[2], label="Explorado (cerrado)"),
    Patch(facecolor=COLORES[3], label="Frontera (abierto)"),
    Patch(facecolor=COLORES[4], label="Nodo actual"),
    Patch(facecolor=COLORES[5], label="Camino optimo"),
    Patch(facecolor=COLORES[6], label="Inicio (S)"),
    Patch(facecolor=COLORES[7], label="Meta (G)"),
]


def matriz_estado(mapa: Mapa, resultado: Resultado, indice: int) -> np.ndarray:
    """
    indice=0 es el estado inicial; el ultimo indice muestra la ruta.
    """
    
    matriz = np.zeros((mapa.filas, mapa.columnas), dtype=int)
    for r, fila in enumerate(mapa.celdas):
        for c, char in enumerate(fila):
            if char == "#":
                matriz[r, c] = 1

    if 1 <= indice <= len(resultado.pasos):
        paso = resultado.pasos[indice - 1]
        for r, c in paso.explorados:
            matriz[r, c] = 2
        for r, c in paso.frontera:
            matriz[r, c] = 3
        if indice == len(resultado.pasos) and resultado.ruta:
            for r, c in resultado.ruta:
                matriz[r, c] = 5
        else:
            r, c = paso.actual
            matriz[r, c] = 4

    matriz[mapa.inicio] = 6
    matriz[mapa.meta] = 7
    return matriz


class VisorAEstrella:
    def __init__(self, mapa: Mapa, a: Resultado, b: Resultado) -> None:
        self.mapa, self.a, self.b = mapa, a, b
        self.indice = 0
        self.reproduciendo = True
        self.fig = plt.figure(figsize=(15, 8.3), constrained_layout=True)
        cuadricula = self.fig.add_gridspec(1, 2, width_ratios=[4.6, 1.4])
        self.ax = self.fig.add_subplot(cuadricula[0, 0])
        self.info = self.fig.add_subplot(cuadricula[0, 1])
        self.info.axis("off")
        self.img = self.ax.imshow(matriz_estado(mapa, a, 0), cmap=CMAP, norm=NORM)
        self.ax.set_aspect("equal")
        self.ax.set_xticks(range(mapa.columnas))
        self.ax.set_yticks(range(mapa.filas))
        self.ax.tick_params(labelsize=7, length=0)
        self.ax.set_xticks(np.arange(-0.5, mapa.columnas, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, mapa.filas, 1), minor=True)
        self.ax.grid(which="minor", color="#FFFFFF", linewidth=0.7)
        self.ax.tick_params(which="minor", bottom=False, left=False)
        self.ax.set_xlabel("Columna (indice desde 0)")
        self.ax.set_ylabel("Fila (indice desde 0)")
        self.ax.set_title("A* | expansion de nodos", fontsize=17, fontweight="bold", pad=17)
        self.marcadores = []
        for posicion, etiqueta in ((mapa.inicio, "S"), (mapa.meta, "G")):
            r, c = posicion
            self.marcadores.append(self.ax.text(c, r, etiqueta, ha="center", va="center", fontsize=10, fontweight="bold", color="white"))
        self.numeros = {}
        for r in range(mapa.filas):
            for c in range(mapa.columnas):
                if mapa.es_transitable((r, c)) and (r, c) not in (mapa.inicio, mapa.meta):
                    self.numeros[(r, c)] = self.ax.text(c, r, "", ha="center", va="center", fontsize=6.5, color="#203248")
        self.caja_info = self.info.text(0.02, 0.99, "", va="top", ha="left", fontsize=11, family="monospace", transform=self.info.transAxes, linespacing=1.5)
        self.info.legend(handles=LEYENDA, loc="lower left", bbox_to_anchor=(0, 0.02), frameon=False, fontsize=10)
        self.fig.canvas.mpl_connect("key_press_event", self._tecla)
        self.dibujar(0)

    def dibujar(self, indice: int) -> None:
        self.indice = max(0, min(indice, len(self.a.pasos)))
        self.img.set_data(matriz_estado(self.mapa, self.a, self.indice))
        for txt in self.numeros.values():
            txt.set_text("")
        if self.indice == 0:
            mensaje = (
                "ANTES DE BUSCAR\n"
                "A* conoce el mapa,\n"
                "su inicio y la meta.\n\n"
                "Selecciona el nodo\n"
                "con menor f = g + h.\n\n"
                f"A*: {self.a.explorados} expandidos\n"
                f"BFS: {self.b.explorados} expandidos\n\n"
                "ESPACIO: pausar\n"
                "FLECHAS: retroceder/avanzar\n"
                "R: reiniciar"
            )
        else:
            paso = self.a.pasos[self.indice - 1]
            final = self.indice == len(self.a.pasos)
            if not final:
                for orden, pos in enumerate(paso.orden_expansion, start=1):
                    if pos in self.numeros:
                        self.numeros[pos].set_text(str(orden))
            ultimos = list(enumerate(paso.orden_expansion, start=1))[-5:]
            historial = "\n".join(f" {n:>3}. {pos}" for n, pos in ultimos)
            mensaje = (
                ("RUTA ENCONTRADA" if final and self.a.ruta else "BUSCANDO RUTA") + "\n"
                f"Paso: {self.indice}/{len(self.a.pasos)}\n"
                f"Nodo: {paso.actual}\n\n"
                f"g = {paso.g:>3}  costo acumulado\n"
                f"h = {paso.h:>3}  Manhattan\n"
                f"f = {paso.f:>3}  g + h\n\n"
                f"Expandidos: {len(paso.explorados)}\n"
                f"En frontera: {len(paso.frontera)}\n\n"
                "ULTIMOS NODOS:\n"
                f"{historial}\n\n"
                f"A*: {self.a.explorados} vs BFS: {self.b.explorados}\n"
                f"Costo de ruta: {self.a.costo}"
            )
        self.caja_info.set_text(mensaje)
        self.fig.canvas.draw_idle()

    def _tecla(self, event) -> None:
        if event.key == " ":
            self.reproduciendo = not self.reproduciendo
        elif event.key == "right":
            self.reproduciendo = False
            self.dibujar(self.indice + 1)
        elif event.key == "left":
            self.reproduciendo = False
            self.dibujar(self.indice - 1)
        elif event.key == "r":
            self.reproduciendo = False
            self.dibujar(0)

    def tick(self, _frame: int) -> None:
        if self.reproduciendo and self.indice < len(self.a.pasos):
            self.dibujar(self.indice + 1)


def mostrar_animacion(mapa: Mapa, a: Resultado, b: Resultado, intervalo: int = 140) -> None:
    visor = VisorAEstrella(mapa, a, b)
    # Mantener la referencia previene que matplotlib libere la animacion.
    anim = FuncAnimation(visor.fig, visor.tick, interval=intervalo, cache_frame_data=False)
    visor._anim = anim
    plt.show()


def guardar_evidencias(mapa: Mapa, a: Resultado, b: Resultado, carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    visor = VisorAEstrella(mapa, a, b)
    visor.dibujar(len(a.pasos))
    visor.fig.savefig(carpeta / "01_ruta_final.png", dpi=150)
    plt.close(visor.fig)

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    valores = [a.explorados, b.explorados]
    barras = ax.bar(["A* (informada)", "BFS (no informada)"], valores, color=["#218E82", "#F1A35F"], width=0.55)
    for barra, valor in zip(barras, valores):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 2, str(valor), ha="center", fontweight="bold")
    ax.set_ylim(0, max(valores) * 1.20)
    ax.set_ylabel("Numero de nodos expandidos")
    ax.set_title("A* vs BFS | mismo laberinto y costo optimo", fontsize=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.5, -0.20, f"Ambos encuentran una ruta de costo {a.costo}.", ha="center", transform=ax.transAxes, fontsize=10)
    fig.savefig(carpeta / "02_comparacion.png", dpi=150)
    plt.close(fig)


def guardar_gif(mapa: Mapa, a: Resultado, b: Resultado, carpeta: Path) -> Path:
    """Exporta un GIF ligero mostrando las expansiones sin depender de la GUI."""
    from PIL import Image, ImageDraw, ImageFont

    carpeta.mkdir(parents=True, exist_ok=True)
    celda = 28
    origen_x, origen_y = 18, 62
    x_panel = origen_x + mapa.columnas * celda + 30
    anchura = x_panel + 300
    altura = max(origen_y + mapa.filas * celda + 55, 610)

    def fuente(tamano: int):
        try:
            return ImageFont.truetype("DejaVuSans.ttf", tamano)
        except OSError:
            return ImageFont.load_default()

    letra = fuente(12)
    numero = fuente(10)
    titulo = fuente(24)
    negrita = fuente(16)
    total = len(a.pasos)
    indices = list(range(0, total + 1, 2))
    if indices[-1] != total:
        indices.append(total)

    cuadros = []
    for indice in indices:
        im = Image.new("RGB", (anchura, altura), "#F9FAFC")
        d = ImageDraw.Draw(im)
        d.text((origen_x, 18), "A* | Busqueda paso a paso", fill="#172638", font=titulo)
        matriz = matriz_estado(mapa, a, indice)
        orden = {}
        if indice:
            paso = a.pasos[indice - 1]
            if indice != total:
                orden = {pos: i for i, pos in enumerate(paso.orden_expansion, start=1)}
        for r in range(mapa.filas):
            for c in range(mapa.columnas):
                x0 = origen_x + c * celda
                y0 = origen_y + r * celda
                x1, y1 = x0 + celda - 1, y0 + celda - 1
                pos = (r, c)
                d.rectangle((x0, y0, x1, y1), fill=COLORES[int(matriz[r, c])])
                etiqueta = "S" if pos == mapa.inicio else "G" if pos == mapa.meta else str(orden[pos]) if pos in orden else ""
                if etiqueta:
                    ft = negrita if etiqueta in ("S", "G") else numero
                    color = "white" if etiqueta in ("S", "G") else "#263347"
                    caja = d.textbbox((0, 0), etiqueta, font=ft)
                    w, h = caja[2] - caja[0], caja[3] - caja[1]
                    d.text((x0 + (celda-w)/2, y0 + (celda-h)/2 - 2), etiqueta, fill=color, font=ft)

        if indice:
            paso = a.pasos[indice - 1]
            lineas = [
                "RUTA ENCONTRADA" if indice == total and a.ruta else "BUSQUEDA EN CURSO",
                f"Paso: {indice}/{total}",
                f"Nodo actual: {paso.actual}",
                "",
                f"g(n) = {paso.g}  (real)",
                f"h(n) = {paso.h}  (estimado)",
                f"f(n) = {paso.f}  (prioridad)",
                "",
                f"Explorados: {len(paso.explorados)}",
                f"Frontera: {len(paso.frontera)}",
                "",
                f"Ruta optima: {a.costo} pasos",
                f"A*: {a.explorados} nodos",
                f"BFS: {b.explorados} nodos",
            ]
        else:
            lineas = [
                "INICIO DE LA BUSQUEDA", "", "Seleccionar menor:",
                "f(n) = g(n) + h(n)", "", "Heuristica: Manhattan",
                "", "Solo 4 direcciones", "Costo por movimiento: 1",
            ]
        for i, linea in enumerate(lineas):
            if i == 0:
                d.text((x_panel, 68), linea, fill="#1A2E42", font=negrita)
            else:
                d.text((x_panel, 68 + i * 31), linea, fill="#263347", font=letra)

        leyenda = "Azul: explorado   Naranja: frontera   Verde: ruta   Morado: actual"
        d.text((origen_x, altura - 32), leyenda, fill="#34465E", font=letra)
        cuadros.append(im)

    ruta = carpeta / "03_busqueda_animada.gif"
    cuadros[0].save(
        ruta,
        save_all=True,
        append_images=cuadros[1:],
        optimize=True,
        duration=130,
        loop=0,
    )
    return ruta
