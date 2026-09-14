# ==============================================================================
# SECCIÓN 1: DATOS COMPARTIDOS (Grafo y Heurística)
# ==============================================================================

# Representamos el grafo dirigido mediante un diccionario.
# La clave es el nodo origen, y el valor es una lista de tuplas (destino, costo).
GRAFO = {
    "S": [("A", 2), ("B", 2)],
    "A": [("C", 2), ("D", 5)],
    "B": [("D", 2)],
    "C": [("G", 3)],
    "D": [("G", 6)],
    "G": []  # El objetivo no tiene salidas
}

# Heurística h(n): Estimación del costo restante hasta llegar al objetivo G.
HEURISTICA = {
    "S": 7,
    "A": 5,
    "B": 7,
    "C": 3,
    "D": 6,
    "G": 0
}

# ==============================================================================
# SECCIÓN 2: FUNCIONES COMPARTIDAS POR TODOS LOS ALGORITMOS
# ==============================================================================

def crear_nodo(estado, padre=None, accion=None, g=0, h=0, prioridad=0):
    """
    Crea y devuelve un 'objeto' (diccionario) que representa un nodo del árbol de búsqueda.
    """
    return {
        "estado": estado,       # Nombre del estado (ej: "S", "A")
        "padre": padre,         # Referencia al nodo anterior para reconstruir el camino
        "accion": accion,       # Transición efectuada (ej: "S -> A")
        "g": g,                 # Costo acumulado desde el inicio
        "h": h,                 # Valor heurístico
        "f": g + h,             # Prioridad total para A*
        "prioridad": prioridad  # Criterio específico con el que se ordenará en la frontera
    }

def obtener_sucesores(estado):
    """
    Devuelve la lista de vecinos alcanzables desde 'estado' junto con su costo.
    .get(estado, []) evita errores si el estado no tiene salidas.
    """
    return GRAFO.get(estado, [])

def reconstruir_camino(nodo_final):
    """
    Recorre los punteros 'padre' desde el nodo objetivo hasta la raíz ("S")
    para armar la secuencia exacta del camino encontrado.
    """
    camino = []
    actual = nodo_final
    while actual is not None:
        camino.append(actual["estado"])
        actual = actual["padre"]  # Subimos un nivel en el árbol
    camino.reverse()  # Invertimos la lista para que quede desde el inicio al final
    return camino

def formatear_frontera(frontera):
    """
    Función auxiliar para mostrar la frontera de forma legible en la traza.
    """
    return [f"{n['estado']}(prio={n['prioridad']})" for n in frontera]


# ==============================================================================
# SECCIÓN 3: FUNCIONES EXCLUSIVAS DE CADA ALGORITMO
# ==============================================================================

def busqueda_ucs(inicio, objetivo):
    """
    Algoritmo 1: Costo Uniforme (UCS)
    Prioridad = g (camino más barato recorrido).
    """
    # 1. Crear nodo inicial con prioridad g=0
    raiz = crear_nodo(inicio, g=0, h=HEURISTICA[inicio], prioridad=0)
    frontera = [raiz]
    mejor_g = {inicio: 0}
    
    # Métricas requeridas por el TP
    generados = 1
    expandidos = 0
    max_frontera = 1
    reaperturas = 0
    
    print("\n--- TRAZA UCS (Prioridad: g) ---")
    
    while len(frontera) > 0:
        # Registrar tamaño máximo alcanzado por la frontera
        max_frontera = max(max_frontera, len(frontera))
        
        # Extraer el nodo con menor prioridad (g). Si hay empate, Python extrae el primero (FIFO)
        nodo = min(frontera, key=lambda n: n["prioridad"])
        frontera.remove(nodo)
        
        estado = nodo["estado"]
        g = nodo["g"]
        
        # Descartar si encontramos un camino más barato a este estado anteriormente
        if g > mejor_g[estado]:
            print(f"Obsoleto descartado: {estado} con g={g} (mejor_g actual={mejor_g[estado]})")
            continue
            
        print(f"Expandiendo: {estado} (g={g}) | Frontera: {formatear_frontera(frontera)}")
        
        # Prueba del objetivo AL EXTRAER
        if estado == objetivo:
            return {
                "camino": reconstruir_camino(nodo),
                "costo": g,
                "expandidos": expandidos,
                "generados": generados,
                "max_frontera": max_frontera,
                "reaperturas": reaperturas
            }
            
        expandidos += 1
        
        # Relajar cada transición legal
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            
            # Evaluar si descubrimos un camino mejor hacia el sucesor
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in mejor_g:
                    reaperturas += 1  # Estado ya conocido que se reabre/mejora
                
                mejor_g[sucesor] = nuevo_g
                h_sucesor = HEURISTICA[sucesor]
                
                nuevo_nodo = crear_nodo(
                    estado=sucesor,
                    padre=nodo,
                    accion=f"{estado}->{sucesor}",
                    g=nuevo_g,
                    h=h_sucesor,
                    prioridad=nuevo_g  # UCS usa g como prioridad
                )
                frontera.append(nuevo_nodo)
                generados += 1

    return None  # Fracaso


def busqueda_voraz(inicio, objetivo):
    """
    Algoritmo 2: Búsqueda Voraz por el Mejor Primero
    Prioridad = h (estado que parece más cerca del objetivo).
    """
    h_inicio = HEURISTICA[inicio]
    raiz = crear_nodo(inicio, g=0, h=h_inicio, prioridad=h_inicio)
    frontera = [raiz]
    mejor_g = {inicio: 0}
    
    generados = 1
    expandidos = 0
    max_frontera = 1
    reaperturas = 0
    
    print("\n--- TRAZA VORAZ (Prioridad: h) ---")
    
    while len(frontera) > 0:
        max_frontera = max(max_frontera, len(frontera))
        nodo = min(frontera, key=lambda n: n["prioridad"])
        frontera.remove(nodo)
        
        estado = nodo["estado"]
        g = nodo["g"]
        h = nodo["h"]
        
        print(f"Expandiendo: {estado} (h={h}) | Frontera: {formatear_frontera(frontera)}")
        
        if estado == objetivo:
            return {
                "camino": reconstruir_camino(nodo),
                "costo": g,
                "expandidos": expandidos,
                "generados": generados,
                "max_frontera": max_frontera,
                "reaperturas": reaperturas
            }
            
        expandidos += 1
        
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in mejor_g:
                    reaperturas += 1
                
                mejor_g[sucesor] = nuevo_g
                h_sucesor = HEURISTICA[sucesor]
                
                nuevo_nodo = crear_nodo(
                    estado=sucesor,
                    padre=nodo,
                    accion=f"{estado}->{sucesor}",
                    g=nuevo_g,
                    h=h_sucesor,
                    prioridad=h_sucesor  # Voraz usa h como prioridad
                )
                frontera.append(nuevo_nodo)
                generados += 1

    return None


def busqueda_a_estrella(inicio, objetivo):
    """
    Algoritmo 3: Búsqueda A*
    Prioridad = f = g + h (costo total estimado de la solución).
    """
    h_inicio = HEURISTICA[inicio]
    raiz = crear_nodo(inicio, g=0, h=h_inicio, prioridad=0 + h_inicio)
    frontera = [raiz]
    mejor_g = {inicio: 0}
    
    generados = 1
    expandidos = 0
    max_frontera = 1
    reaperturas = 0
    
    print("\n--- TRAZA A* (Prioridad: g + h) ---")
    
    while len(frontera) > 0:
        max_frontera = max(max_frontera, len(frontera))
        nodo = min(frontera, key=lambda n: n["prioridad"])
        frontera.remove(nodo)
        
        estado = nodo["estado"]
        g = nodo["g"]
        f = nodo["f"]
        
        if g > mejor_g[estado]:
            print(f"Obsoleto descartado: {estado} con g={g} (mejor_g actual={mejor_g[estado]})")
            continue
            
        print(f"Expandiendo: {estado} (f={f}) | Frontera: {formatear_frontera(frontera)}")
        
        if estado == objetivo:
            return {
                "camino": reconstruir_camino(nodo),
                "costo": g,
                "expandidos": expandidos,
                "generados": generados,
                "max_frontera": max_frontera,
                "reaperturas": reaperturas
            }
            
        expandidos += 1
        
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in mejor_g:
                    reaperturas += 1
                
                mejor_g[sucesor] = nuevo_g
                h_sucesor = HEURISTICA[sucesor]
                
                nuevo_nodo = crear_nodo(
                    estado=sucesor,
                    padre=nodo,
                    accion=f"{estado}->{sucesor}",
                    g=nuevo_g,
                    h=h_sucesor,
                    prioridad=nuevo_g + h_sucesor  # A* usa g + h como prioridad
                )
                frontera.append(nuevo_nodo)
                generados += 1

    return None


# ==============================================================================
# SECCIÓN 4: EJECUCIÓN Y TABLA COMPARATIVA
# ==============================================================================

# Ejecutamos los 3 algoritmos desde "S" hasta "G"
res_ucs = busqueda_ucs("S", "G")
res_voraz = busqueda_voraz("S", "G")
res_a_star = busqueda_a_estrella("S", "G")

# Formateamos la tabla requerida en la Sección 5 del TP
print("\n" + "="*75)
print(" TABLA COMPARATIVA DE RESULTADOS")
print("="*75)
print(f"{'Resultado':<22} | {'UCS':<15} | {'Voraz':<15} | {'A*':<15}")
print("-" * 75)
print(f"{'Camino':<22} | {str(res_ucs['camino']):<15} | {str(res_voraz['camino']):<15} | {str(res_a_star['camino']):<15}")
print(f"{'Costo':<22} | {res_ucs['costo']:<15} | {res_voraz['costo']:<15} | {res_a_star['costo']:<15}")
print(f"{'Prioridad':<22} | {'g':<15} | {'h':<15} | {'g+h':<15}")
print(f"{'Expandidos (antes G)':<22} | {res_ucs['expandidos']:<15} | {res_voraz['expandidos']:<15} | {res_a_star['expandidos']:<15}")
print(f"{'Estados Generados':<22} | {res_ucs['generados']:<15} | {res_voraz['generados']:<15} | {res_a_star['generados']:<15}")
print(f"{'Frontera Máxima':<22} | {res_ucs['max_frontera']:<15} | {res_voraz['max_frontera']:<15} | {res_a_star['max_frontera']:<15}")
print(f"{'Reaperturas':<22} | {res_ucs['reaperturas']:<15} | {res_voraz['reaperturas']:<15} | {res_a_star['reaperturas']:<15}")
print("="*75)