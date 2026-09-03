"""Parte 3: Construcción y Procesamiento de la Bitácora de Agentes de Movilidad.

Este módulo implementa el bucle de simulación temporal paso a paso para comparar
un Agente Reactivo Simple frente a un Agente Reactivo Basado en Modelo.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
from pathlib import Path

# Importamos las funciones de decisión y estado de la plantilla
from plantilla_agentes_movilidad import (
    decidir_reactivo_simple,
    crear_estado_inicial,
    actualizar_estado,
    decidir_reactivo_modelo,
)


def procesar_secuencia(percepciones: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta ambos agentes a lo largo del tiempo y construye la bitácora comparativa.

    Reglas de causalidad temporal:
    - Se recorren las observaciones estrictamente en orden cronológico (hora a hora).
    - Cada decisión solo tiene acceso a la percepción de la hora h y (en el caso del
      agente basado en modelo) a su estado interno acumulado hasta h.
    - No se consulta bajo ninguna circunstancia información futura (h + 1).

    Args:
        percepciones: DataFrame con las observaciones horarias (debe contener 'hora' y 'presion').

    Returns:
        DataFrame con la bitácora comparativa según la especificación de la consigna.
    """
    # 1. Asegurar el orden cronológico estricto sin alterar el DataFrame original
    df_ordenado = percepciones.sort_values(by="hora").copy()

    # 2. Inicializar la memoria (estado interno) del agente basado en modelo
    estado_modelo = crear_estado_inicial()

    registros_bitacora: list[dict[str, Any]] = []

    # 3. Bucle temporal: procesar una hora a la vez
    for _, fila in df_ordenado.iterrows():
        percepcion = fila.to_dict()
        hora_actual = percepcion.get("hora")
        presion_actual = percepcion.get("presion")

        # --- Agente 1: Reactivo Simple (Sin memoria) ---
        accion_simple, motivo_simple = decidir_reactivo_simple(percepcion)

        # --- Agente 2: Reactivo Basado en Modelo (Con memoria) ---
        # Paso A: Percibir y actualizar el estado interno con la nueva observación
        estado_modelo = actualizar_estado(estado_modelo, percepcion)

        # Paso B: Decidir usando exclusivamente el estado actualizado
        accion_modelo, motivo_modelo = decidir_reactivo_modelo(estado_modelo)

        # Paso C: Registrar la acción tomada en el estado interno para persistencia
        estado_modelo["ultima_accion"] = accion_modelo

        # --- Registrar en la Bitácora ---
        registros_bitacora.append(
            {
                "hora": hora_actual,
                "presion": presion_actual,
                "racha_presion_alta": estado_modelo.get("racha_presion_alta", 0),
                "accion_simple": accion_simple,
                "motivo_simple": motivo_simple,
                "accion_modelo": accion_modelo,
                "motivo_modelo": motivo_modelo,
            }
        )

    # 4. Construir y devolver el DataFrame resultante de la bitácora
    columnas = [
        "hora",
        "presion",
        "racha_presion_alta",
        "accion_simple",
        "motivo_simple",
        "accion_modelo",
        "motivo_modelo",
    ]
    return pd.DataFrame(registros_bitacora, columns=columnas)


def imprimir_bitacora_consola(df_bitacora: pd.DataFrame) -> None:
    """Imprime la bitácora en la consola con un formato visual claro, ordenado y legible."""
    ancho = 90
    print("\n" + "=" * ancho)
    print(" BITACORA COMPARATIVA DE AGENTES DE MOVILIDAD ".center(ancho, "="))
    print("=" * ancho)

    # Vista detallada paso a paso por hora
    for _, fila in df_bitacora.iterrows():
        hora = int(fila["hora"]) if pd.notnull(fila["hora"]) else "N/A"
        presion = f"{fila['presion']:.2f}" if pd.notnull(fila["presion"]) else "N/A"
        racha = int(fila["racha_presion_alta"]) if pd.notnull(fila["racha_presion_alta"]) else 0

        print(f"\n[+] HORA: {hora:02d}:00  |  Presion: {presion}  |  Racha alta acumulada: {racha}h")
        print("-" * ancho)
        print(f"  * [Agente Simple]  -> Accion: {fila['accion_simple']}")
        print(f"                        Motivo: {fila['motivo_simple']}")
        print(f"  * [Agente Modelo]  -> Accion: {fila['accion_modelo']}")
        print(f"                        Motivo: {fila['motivo_modelo']}")

    print("\n" + "=" * ancho)
    print(" VISTA TABULAR RESUMIDA ".center(ancho, "-"))
    print("=" * ancho)

    # Formateo compacto de tabla
    header = f"{'Hora':^7} | {'Presion':^9} | {'Racha':^7} | {'Agente Simple':^22} | {'Agente Modelo':^22}"
    separator = "--------+-----------+---------+------------------------+------------------------"
    print(header)
    print(separator)

    for _, fila in df_bitacora.iterrows():
        hora = f"{int(fila['hora']):02d}:00" if pd.notnull(fila["hora"]) else "N/A"
        presion = f"{fila['presion']:.2f}" if pd.notnull(fila["presion"]) else "N/A"
        racha = f"{int(fila['racha_presion_alta'])}h" if pd.notnull(fila["racha_presion_alta"]) else "0h"
        simple = str(fila["accion_simple"])
        modelo = str(fila["accion_modelo"])
        print(f"{hora:^7} | {presion:^9} | {racha:^7} | {simple:<22} | {modelo:<22}")

    print("=" * ancho + "\n")



def ejecutar_demostracion(
    ruta_percepciones: str = "escenario_agente/percepciones.csv",
    ruta_salida: str = "bitacora_agentes.csv",
) -> pd.DataFrame:
    """Carga un escenario reproducible, procesa la secuencia y muestra los resultados."""
    archivo_csv = Path(ruta_percepciones)
    if not archivo_csv.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de percepciones en '{ruta_percepciones}'. "
            "Asegúrate de generar el escenario previo con 'simulador_entorno_agente.py'."
        )

    df_percepciones = pd.read_csv(archivo_csv)
    bitacora = procesar_secuencia(df_percepciones)

    # Guardar en CSV para cumplir con los requerimientos de entrega
    bitacora.to_csv(ruta_salida, index=False)

    # Mostrar de forma visualmente atractiva y legible en consola
    imprimir_bitacora_consola(bitacora)

    return bitacora


if __name__ == "__main__":
    try:
        df_bitacora = ejecutar_demostracion()
    except Exception as e:
        print(f"Error al ejecutar la demostración: {e}")


# ==============================================================================
# RESPUESTAS A LAS PREGUNTAS DE LA PARTE 3 (CONSIGNA)
# ==============================================================================
"""
1. ¿En qué situaciones ambos agentes producen la misma acción?
   - Presión baja (< 0.85): Ambos concluyen NO_REFORZAR.
   - Presión alta persistente (>= 2 horas consecutivas con presión >= 0.85): Ambos concluyen RECOMENDAR_REFUERZO.
   - Datos inválidos o faltantes: Ambos concluyen ABSTENERSE.

2. ¿Cuándo reaccionan de forma diferente?
   - En la primera hora de presión alta (racha == 1): El agente simple reacciona de inmediato
     con RECOMENDAR_REFUERZO al ver el umbral superado en el instante t. En cambio, el agente
     basado en modelo devuelve NO_REFORZAR porque su memoria indica que aún no hay persistencia temporal.

3. ¿Por qué el segundo agente está basado en modelo aunque no planifique?
   - Porque mantiene un estado interno (memoria del mundo) que resume la historia pasada
     (como 'racha_presion_alta') para rastrear aspectos que no se pueden observar en la
     sola percepción del instante actual t.
   - Según la definición formal (Russell & Norvig), un agente basado en modelo es aquel cuya
     función de decisión depende de un estado interno que modela cómo evoluciona el entorno,
     sin requerir necesariamente búsqueda de caminos, simulación de futuros ni planificación.


4. ¿Qué representa 'tasa_otras_simulada' y qué no permite afirmar?
   - Representa la proporción sintética y estocástica de viajes asignada a otras empresas en la simulación didáctica.
   - NO permite afirmar la cantidad real de taxis competidores ni la cuota de mercado real, ya que los datos
     TLC originales solo contienen viajes Yellow Taxi realizados y la partición competitiva es puramente sintética.

5. ¿Por qué 'resultado_h_mas_1.csv' no puede formar parte de la percepción?
   - Porque contiene datos del futuro (hora h+1) que aún no han ocurrido en el momento de tomar la decisión en h.
   - Consultarlo violaría el principio de causalidad temporal (fuga de información / data leakage),
     haciendo que el agente decida con clarividencia en lugar de evaluar bajo incertidumbre en tiempo real.
"""


