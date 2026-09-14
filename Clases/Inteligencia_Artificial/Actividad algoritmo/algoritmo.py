# ==============================================================================
# SECCIÓN 1: DATOS COMPARTIDOS (Grafo y Heurística)
# ==============================================================================

ESTUDIANTE = "Johann Beskow 36923"
CURSO = "Inteligencia Artificial"

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
    return [
        f"{n['estado']}(g={n['g']},h={n['h']},f={n['f']},prio={n['prioridad']})"
        for n in frontera
    ]


def extraer_mejor(frontera):
    """Extrae el menor valor; ante empate conserva el orden FIFO de inserción."""
    indice, nodo = min(
        enumerate(frontera), key=lambda elemento: (elemento[1]["prioridad"], elemento[0])
    )
    frontera.pop(indice)
    return nodo


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
    estados_expandidos = set()
    
    print("\n--- TRAZA UCS (Prioridad: g) ---")
    
    while len(frontera) > 0:
        # Registrar tamaño máximo alcanzado por la frontera
        max_frontera = max(max_frontera, len(frontera))
        
        # Menor g; el desempate es FIFO.
        nodo = extraer_mejor(frontera)
        
        estado = nodo["estado"]
        g = nodo["g"]
        
        # Descartar si encontramos un camino más barato a este estado anteriormente
        if g > mejor_g[estado]:
            print(f"Obsoleto descartado: {estado} con g={g} (mejor_g actual={mejor_g[estado]})")
            continue
            
        print(
            f"Expandiendo: {estado} (g={g}, h={nodo['h']}, f={nodo['f']}, "
            f"prio={nodo['prioridad']}) | Frontera: {formatear_frontera(frontera)}"
        )
        
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
        estados_expandidos.add(estado)
        
        # Relajar cada transición legal
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            
            # Evaluar si descubrimos un camino mejor hacia el sucesor
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in estados_expandidos:
                    reaperturas += 1  # Solo cuenta si ya había sido expandido.
                
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
    estados_expandidos = set()
    
    print("\n--- TRAZA VORAZ (Prioridad: h) ---")
    
    while len(frontera) > 0:
        max_frontera = max(max_frontera, len(frontera))
        nodo = extraer_mejor(frontera)
        
        estado = nodo["estado"]
        g = nodo["g"]
        h = nodo["h"]

        if g > mejor_g[estado]:
            print(f"Obsoleto descartado: {estado} con g={g} (mejor_g actual={mejor_g[estado]})")
            continue
        
        print(
            f"Expandiendo: {estado} (g={g}, h={h}, f={nodo['f']}, "
            f"prio={nodo['prioridad']}) | Frontera: {formatear_frontera(frontera)}"
        )
        
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
        estados_expandidos.add(estado)
        
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in estados_expandidos:
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
    estados_expandidos = set()
    
    print("\n--- TRAZA A* (Prioridad: g + h) ---")
    
    while len(frontera) > 0:
        max_frontera = max(max_frontera, len(frontera))
        nodo = extraer_mejor(frontera)
        
        estado = nodo["estado"]
        g = nodo["g"]
        f = nodo["f"]
        
        if g > mejor_g[estado]:
            print(f"Obsoleto descartado: {estado} con g={g} (mejor_g actual={mejor_g[estado]})")
            continue
            
        print(
            f"Expandiendo: {estado} (g={g}, h={nodo['h']}, f={f}, "
            f"prio={nodo['prioridad']}) | Frontera: {formatear_frontera(frontera)}"
        )
        
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
        estados_expandidos.add(estado)
        
        for sucesor, costo in obtener_sucesores(estado):
            nuevo_g = g + costo
            if sucesor not in mejor_g or nuevo_g < mejor_g[sucesor]:
                if sucesor in estados_expandidos:
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
print(f"Estudiante: {ESTUDIANTE}")
print(f"Curso: {CURSO}")
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


# ==============================================================================
# SECCIÓN 5: RESPUESTAS DE ANÁLISIS
# ==============================================================================

print("\nRESPUESTAS DE ANÁLISIS")
print("1. Voraz y A* coinciden porque, desde S, la heurística prioriza A sobre B "
    "(5 < 7) y, desde A, prioriza C sobre D (3 < 6). Además, los costos y "
    "la heurística de este grafo hacen que A* mantenga f=7 en el camino "
    "óptimo; h es admisible y consistente en las aristas de este ejemplo. "
    "La admisibilidad por sí sola no garantiza que voraz sea óptimo.")
print("2. No. Voraz prioriza únicamente h(n), que estima lo que falta y no "
    "incluye el costo g(n) ya pagado. Puede elegir un estado aparentemente "
    "cercano al objetivo pero situado al final de un camino caro, por lo que "
    "no garantiza el menor costo.")
print("3. Si h=0 para todos los estados, la prioridad de A* queda f=g+0=g. "
    "Por lo tanto, A* coincide con UCS (búsqueda de costo uniforme).")
print("4. No hubo reaperturas en ninguno de los tres algoritmos: una reapertura "
    "exige mejorar el costo de un estado después de que ya fue expandido. "
    "En UCS, D sí fue descubierto con g=7 y luego mejorado a g=4 antes de "
    "expandirse; eso es una actualización de frontera, no una reapertura. "
    "La entrada vieja se descarta como obsoleta.")
print("5. No. Expandir menos estados mide esfuerzo de búsqueda, no costo de la "
    "solución. Aquí voraz expande 3 estados antes de G y obtiene costo 7, "
    "mientras UCS expande 5 y garantiza el menor costo; en otro grafo voraz "
    "podría expandir menos y devolver un camino más caro.")