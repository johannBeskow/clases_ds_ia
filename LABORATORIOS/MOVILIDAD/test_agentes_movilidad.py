import math
from pathlib import Path

import pandas as pd

from agentes_movilidad import (
    actualizar_estado,
    crear_estado_inicial,
    decidir_reactivo_modelo,
    decidir_reactivo_simple,
    procesar_secuencia,
)


def percepcion(hora, presion, capacidad=20):
    return {"hora": hora, "presion": presion, "capacidad_x": capacidad}


def test_presion_baja_ambos_no_refuerzan():
    actual = percepcion(6, 0.50)
    accion_simple, _ = decidir_reactivo_simple(actual)
    estado = actualizar_estado(crear_estado_inicial(), actual)
    accion_modelo, _ = decidir_reactivo_modelo(estado)

    assert accion_simple == "NO_REFORZAR"
    assert accion_modelo == "NO_REFORZAR"


def test_primera_hora_alta_difiere():
    actual = percepcion(6, 1.10)
    accion_simple, _ = decidir_reactivo_simple(actual)
    estado = actualizar_estado(crear_estado_inicial(), actual)
    accion_modelo, _ = decidir_reactivo_modelo(estado)

    assert accion_simple == "RECOMENDAR_REFUERZO"
    assert accion_modelo == "NO_REFORZAR"


def test_segunda_hora_alta_ambos_recomiendan():
    estado = actualizar_estado(crear_estado_inicial(), percepcion(6, 1.10))
    estado = actualizar_estado(estado, percepcion(7, 1.20))
    accion_modelo, _ = decidir_reactivo_modelo(estado)

    assert accion_modelo == "RECOMENDAR_REFUERZO"


def test_misma_percepcion_historias_distintas():
    final = percepcion(8, 1.10)
    estado_sin_historia = actualizar_estado(crear_estado_inicial(), final)
    estado_con_historia = actualizar_estado(
        actualizar_estado(crear_estado_inicial(), percepcion(7, 1.10)),
        final,
    )

    simple_a, _ = decidir_reactivo_simple(final)
    simple_b, _ = decidir_reactivo_simple(final)
    modelo_a, _ = decidir_reactivo_modelo(estado_sin_historia)
    modelo_b, _ = decidir_reactivo_modelo(estado_con_historia)

    assert simple_a == simple_b
    assert modelo_a != modelo_b


def test_datos_invalidos_producen_abstencion():
    casos = [
        percepcion(6, "alta"),
        percepcion(6, math.nan),
        percepcion(6, 1.0, 0),
        percepcion(6, 1.0, math.nan),
    ]

    for actual in casos:
        accion_simple, _ = decidir_reactivo_simple(actual)
        estado = actualizar_estado(crear_estado_inicial(), actual)
        accion_modelo, _ = decidir_reactivo_modelo(estado)
        assert accion_simple == "ABSTENERSE"
        assert accion_modelo == "ABSTENERSE"


def test_evaluacion_h_mas_1_es_real_y_no_se_usa_para_decidir():
    carpeta = Path(__file__).parent
    percepciones = pd.read_csv(carpeta / "escenario_agente" / "percepciones.csv")
    evaluacion = pd.read_csv(carpeta / "escenario_agente" / "resultado_h_mas_1.csv")
    percepcion_h = percepciones.sort_values("hora").iloc[-1].to_dict()
    fila_h_mas_1 = evaluacion.sort_values("hora").iloc[0].to_dict()

    assert fila_h_mas_1["hora"] == percepcion_h["hora"] + 1
    estado_h = actualizar_estado(crear_estado_inicial(), percepcion_h)
    accion_simple, _ = decidir_reactivo_simple(percepcion_h)
    accion_modelo, _ = decidir_reactivo_modelo(estado_h)

    assert accion_simple in {"NO_REFORZAR", "RECOMENDAR_REFUERZO"}
    assert accion_modelo in {"NO_REFORZAR", "RECOMENDAR_REFUERZO"}
    assert "resultado_h_mas_1" not in str(percepcion_h)


def test_bitacora_contiene_campos_requeridos():
    carpeta = Path(__file__).parent
    percepciones = pd.read_csv(carpeta / "escenario_agente" / "percepciones.csv")
    bitacora = procesar_secuencia(percepciones)
    campos = {
        "hora",
        "presion",
        "racha_presion_alta",
        "accion_simple",
        "motivo_simple",
        "accion_modelo",
        "motivo_modelo",
    }

    assert campos.issubset(bitacora.columns)
