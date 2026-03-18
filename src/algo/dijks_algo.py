
class Algorithm:
    def __init__(self, data) -> None:
        self.data = data

    def process_algo(self):
        start_zone = next((z for z in self.data.zones if z.role == "START"), None)
        end_zone = next((z for z in self.data.zones if z.role == "END"), None)
        distancias = {z: float('inf') for z in self.data.zones}
        padres = {z: None for z in self.data.zones}
        nodos_pendientes = list(self.data.zones)
        distancias[start_zone] = 0
        while nodos_pendientes:
            nodo_actual = min(nodos_pendientes, key=lambda z: distancias[z])
            print("NODO ACTUAL", nodo_actual.name)
            if distancias[nodo_actual] == float('inf'):
                break
            if nodo_actual == end_zone:
                break
            nodos_pendientes.remove(nodo_actual)
            for conexion in nodo_actual.connection:
                nombre_vecino = conexion.nodes[0] if conexion.nodes[1] == nodo_actual.name else conexion.nodes[1]
                vecino = next(z for z in self.data.zones if z.name == nombre_vecino)
                print("Soy nombre_Vecino", nombre_vecino)
                print("Soy Vecino", vecino.name)
                if not vecino.has_capacity():
                    continue
                peso_paso = vecino.get_movement_cost()
                print("SOY PESOPESO", peso_paso)
                nueva_distancia = distancias[nodo_actual] + peso_paso
                print(nueva_distancia, distancias[vecino])
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    padres[vecino] = nodo_actual
                print()
        return self.reconstruir_ruta(padres, end_zone)

    def reconstruir_ruta(self, padres, destino):
        ruta = []
        actual = destino
        while actual is not None:
            ruta.append(actual)
            actual = padres[actual]
        return ruta[::-1]
