"""Plantilla para el trabajo practico de agentes de movilidad.

Complete las funciones marcadas con TODO sin consultar datos de h+1.
"""

from __future__ import annotations

import math
from numbers import Real
from typing import Any

import pandas as pd


ACCIONES = {"NO_REFORZAR", "RECOMENDAR_REFUERZO", "ABSTENERSE"}
UMBRAL_PRESION = 0.85


def _percepcion_valida(percepcion: dict[str, Any]) -> bool:
    presion = percepcion.get("presion")
    capacidad = percepcion.get("capacidad_x")
    if (
        isinstance(presion, bool)
        or not isinstance(presion, Real)
        or not math.isfinite(float(presion))
        or presion < 0
        or isinstance(capacidad, bool)
        or not isinstance(capacidad, Real)
        or not math.isfinite(float(capacidad))
        or capacidad <= 0
    ):
        return False
    return True


def decidir_reactivo_simple(percepcion: dict[str, Any]) -> tuple[str, str]:
    """Devuelve (accion, motivo) usando solo la percepcion actual."""
    presion = percepcion.get("presion")
    if not _percepcion_valida(percepcion):
        return ("ABSTENERSE", "Percepción inválida o datos no confiables")
    # Reglas normales
    if presion >= UMBRAL_PRESION:
        return ("RECOMENDAR_REFUERZO", f"Presión {presion:.2f} >= {UMBRAL_PRESION}")
    return ("NO_REFORZAR", f"Presión {presion:.2f} < {UMBRAL_PRESION}")


def crear_estado_inicial() -> dict[str, Any]:
    """Crea el estado persistente del agente reactivo basado en modelo."""
    return {
        "percepcion_valida": False,
        "racha_presion_alta": 0,
        "presion_anterior": None,
        "hora_anterior": None,
        "ultima_accion": None,
    }


def actualizar_estado(
    estado_anterior: dict[str, Any],
    percepcion: dict[str, Any],
) -> dict[str, Any]:
    """Actualiza la memoria a partir del estado anterior y la percepcion."""
    presion = percepcion.get("presion")
    capacidad = percepcion.get("capacidad_x")
    hora = percepcion.get("hora")

    # 1. Validar la percepción
    if not _percepcion_valida(percepcion):
        return {
            "percepcion_valida": False,
            "racha_presion_alta": 0,
            "presion_anterior": None,
            "hora_anterior": None,
            "ultima_accion": estado_anterior.get("ultima_accion"),
        }

    # 2. Verificar si hubo discontinuidad horaria
    hora_anterior = estado_anterior.get("hora_anterior")
    hubo_salto_temporal = (
        hora is not None
        and hora_anterior is not None
        and hora != hora_anterior + 1
    )

    racha_anterior = 0 if hubo_salto_temporal else estado_anterior.get("racha_presion_alta", 0)

    # 3. Si es válida, calcular la nueva racha
    if presion >= UMBRAL_PRESION:
        nueva_racha = racha_anterior + 1
    else:
        nueva_racha = 0

    # 4. Devolver el nuevo estado
    return {
        "percepcion_valida": True,
        "racha_presion_alta": nueva_racha,
        "presion_anterior": presion,
        "hora_anterior": hora,
        "ultima_accion": estado_anterior.get("ultima_accion"),
    }


def decidir_reactivo_modelo(
    estado_actual: dict[str, Any],
) -> tuple[str, str]:
    """Devuelve (accion, motivo) a partir del estado interno actualizado."""
    # 1. Percepción inválida
    if not estado_actual.get("percepcion_valida", False):
        return ("ABSTENERSE", "Percepción inválida o datos no confiables")

    racha = estado_actual.get("racha_presion_alta", 0)
    presion = estado_actual.get("presion_anterior")
    presion_str = f"{presion:.2f}" if isinstance(presion, (int, float)) else "N/A"

    # 2. Dos o más horas consecutivas con presión alta
    if racha >= 2:
        return (
            "RECOMENDAR_REFUERZO",
            f"Presión alta persistente ({racha} horas consecutivas >= {UMBRAL_PRESION}, actual: {presion_str})",
        )

    # 3. Cualquier otro estado válido
    return (
        "NO_REFORZAR",
        f"Presión actual: {presion_str}, racha alta = {racha} (< 2 horas consecutivas)",
    )


def procesar_secuencia(percepciones: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta ambos agentes y construye la bitacora comparativa."""
    df_ordenado = percepciones.sort_values(by="hora").copy()
    estado_modelo = crear_estado_inicial()
    registros: list[dict[str, Any]] = []

    for _, fila in df_ordenado.iterrows():
        percepcion = fila.to_dict()
        hora = percepcion.get("hora")
        presion = percepcion.get("presion")

        # 1. Agente Reactivo Simple
        accion_simple, motivo_simple = decidir_reactivo_simple(percepcion)

        # 2. Agente Reactivo Basado en Modelo
        estado_modelo = actualizar_estado(estado_modelo, percepcion)
        accion_modelo, motivo_modelo = decidir_reactivo_modelo(estado_modelo)
        estado_modelo["ultima_accion"] = accion_modelo

        # 3. Registro
        registros.append(
            {
                "hora": hora,
                "presion": presion,
                "racha_presion_alta": estado_modelo.get("racha_presion_alta", 0),
                "accion_simple": accion_simple,
                "motivo_simple": motivo_simple,
                "accion_modelo": accion_modelo,
                "motivo_modelo": motivo_modelo,
            }
        )

    columnas = [
        "hora",
        "presion",
        "racha_presion_alta",
        "accion_simple",
        "motivo_simple",
        "accion_modelo",
        "motivo_modelo",
    ]
    return pd.DataFrame(registros, columns=columnas)

