"""
Pruebas con unittest incluido en Python
"""

import unittest
from collections import deque

from src.busqueda import a_estrella, bfs, manhattan
from src.mapa import crear_mapa


class TestBusquedas(unittest.TestCase):
    def setUp(self):
        self.mapa = crear_mapa()

    def test_a_estrella_encuentra_ruta_optima(self):
        a = a_estrella(self.mapa)
        b = bfs(self.mapa)
        self.assertEqual(a.ruta[0], self.mapa.inicio)
        self.assertEqual(a.ruta[-1], self.mapa.meta)
        self.assertEqual(a.costo, b.costo)
        self.assertEqual(a.costo, len(a.ruta) - 1)
        for u, v in zip(a.ruta, a.ruta[1:]):
            self.assertIn(v, self.mapa.vecinos(u))

    def test_a_estrella_expande_menos_en_este_mapa(self):
        a, b = a_estrella(self.mapa), bfs(self.mapa)
        self.assertLess(a.explorados, b.explorados)

    def test_manhattan_es_admisible(self):
        # Distancias REALES desde meta; nunca debe superarlas la heuristica.
        distancias = {self.mapa.meta: 0}
        cola = deque([self.mapa.meta])
        while cola:
            actual = cola.popleft()
            for vecino in self.mapa.vecinos(actual):
                if vecino not in distancias:
                    distancias[vecino] = distancias[actual] + 1
                    cola.append(vecino)
        for posicion, distancia_real in distancias.items():
            self.assertLessEqual(manhattan(posicion, self.mapa.meta), distancia_real)

    def test_registro_de_expansiones(self):
        a = a_estrella(self.mapa)
        self.assertEqual(len(a.pasos), a.explorados)
        self.assertEqual(a.pasos[0].actual, self.mapa.inicio)
        self.assertEqual(a.pasos[-1].actual, self.mapa.meta)
        for i, paso in enumerate(a.pasos, start=1):
            self.assertEqual(paso.g + paso.h, paso.f)
            self.assertEqual(len(paso.explorados), i)
            self.assertNotIn(paso.actual, paso.frontera)

    def test_si_no_hay_ruta(self):
        mapa = crear_mapa(("#####", "#S#G#", "#####"))
        a, b = a_estrella(mapa), bfs(mapa)
        self.assertIsNone(a.costo)
        self.assertEqual(a.ruta, ())
        self.assertIsNone(b.costo)


if __name__ == "__main__":
    unittest.main()
