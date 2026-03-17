class Algorithm:
    def __init__(self, data) -> None:
        self.data = data

    def process_algo(self):
        start = next((z for z in self.data.zones if z.role == "START"), None)
        end = next((z for z in self.data.zones if z.role == "END"), None)
        distancias = {start: 0}
        queue = [(0, start)]

