class Variable:
    def __init__(self, nombre, tipo, fila, col, longitud, dominio):
        self.nombre = nombre
        self.tipo = tipo        # h/v
        self.fila = fila
        self.col = col
        self.longitud = longitud
        self.dominio = dominio
        self.restricciones = [] # lista de tuplas (vecino, pos_propia, pos_vecino)
        self.valor = None
        self.podado = []    # lista de tuplas (palabra_podada, variable_responsable)
        self.conflictos = set()

    def __str__(self):
        return f"Nombre {self.nombre} Posición {self.fila} {self.col} Tipo: {self.tipo} Dominio: {self.dominio} Restricciones: {len(self.restricciones)}"


