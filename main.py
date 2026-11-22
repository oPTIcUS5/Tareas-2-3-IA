"""
Punto de entrada para la Tarea 2.3 de Inteligencia Artificial.
"""

# holeee

import argparse
from pathlib import Path

from src.busqueda import a_estrella, bfs
from src.mapa import crear_mapa


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualizacion de A* comparado con BFS")
    parser.add_argument(
        "--modo", choices=("animacion", "evidencias", "gif", "consola"),
        default="animacion", help="Tipo de demostracion (por defecto: animacion)",
    )
    parser.add_argument("--intervalo", type=int, default=140, help="Milisegundos entre pasos en la ventana")
    parser.add_argument("--detalles", action="store_true", help="Imprime g, h y f de cada expansion")
    args = parser.parse_args()

    if args.intervalo <= 0:
        parser.error("--intervalo debe ser mayor que cero")

    mapa = crear_mapa()
    a = a_estrella(mapa)
    b = bfs(mapa)
    print("\nTAREA 2.3 | A* (heuristica Manhattan) vs BFS")
    print(f"Mapa: {mapa.filas} filas x {mapa.columnas} columnas")
    print(f"Inicio: {mapa.inicio} | Meta: {mapa.meta}")
    print(f"A*: ruta de costo {a.costo}; {a.explorados} nodos expandidos")
    print(f"BFS: ruta de costo {b.costo}; {b.explorados} nodos expandidos")
    if b.explorados:
        print(f"A* expande {(1 - a.explorados / b.explorados) * 100:.1f}% menos nodos que BFS en este mapa.")
    print("\nRuta A*:")
    print(" -> ".join(map(str, a.ruta)) if a.ruta else "No existe ruta")

    if args.detalles:
        print("\nPASOS (g = acumulado, h = Manhattan, f = g+h)")
        for i, paso in enumerate(a.pasos, start=1):
            print(f"{i:03d} | nodo={paso.actual} | g={paso.g:2d} h={paso.h:2d} f={paso.f:2d} | frontera={len(paso.frontera):2d}")

    if args.modo != "consola":
        # Se importa aqui para que --modo consola y las pruebas no requieran GUI.
        from src.visualizacion import guardar_evidencias, guardar_gif, mostrar_animacion
        carpeta = Path(__file__).resolve().parent / "evidencias"
        if args.modo == "animacion":
            print("\nControles: ESPACIO pausa; derecha/izquierda avanza/retrocede; R reinicia.")
            mostrar_animacion(mapa, a, b, args.intervalo)
        elif args.modo == "evidencias":
            guardar_evidencias(mapa, a, b, carpeta)
            print(f"\nImagenes guardadas en: {carpeta}")
        elif args.modo == "gif":
            guardar_evidencias(mapa, a, b, carpeta)
            gif = guardar_gif(mapa, a, b, carpeta)
            print(f"\nCapturas y animacion guardadas en: {gif.parent}")


if __name__ == "__main__":
    main()
