# Informe de agentes de movilidad

## Objetivo

Se comparan un agente reactivo simple y un agente reactivo basado en modelo. Ambos reciben la percepcion horaria de la zona y recomiendan si una persona deberia considerar reforzarla durante la hora siguiente.

## Agentes

El agente reactivo simple usa solamente la percepcion actual. Si la presion es mayor o igual que `0.85`, devuelve `RECOMENDAR_REFUERZO`; si es menor, devuelve `NO_REFORZAR`. Ante datos faltantes, no numericos, no finitos o una capacidad invalida, devuelve `ABSTENERSE`.

El agente basado en modelo conserva un estado interno con la percepcion valida, la presion anterior, la hora anterior y la racha de horas consecutivas con presion alta. Recomienda refuerzo a partir de la segunda hora consecutiva con presion mayor o igual que `0.85`.

## Comparacion

Ambos agentes coinciden cuando la presion es baja, cuando la presion alta persiste durante dos o mas horas consecutivas y cuando la percepcion es invalida. Difieren durante la primera hora de presion alta: el agente simple recomienda de inmediato y el agente basado en modelo espera evidencia temporal adicional.

El segundo agente es basado en modelo porque su decision depende de un estado interno que resume la historia. No necesita planificar ni buscar caminos para pertenecer a esa categoria.

## PEAS

| Elemento | Descripcion |
|---|---|
| Performance | Recomendaciones coherentes, ausencia de fuga temporal, abstencion ante datos invalidos y trazabilidad. |
| Environment | Secuencia simulada de horas de una zona TLC, demanda transformada, flota ficticia de X, otras empresas sinteticas y responsable humano. |
| Actuators | `NO_REFORZAR`, `RECOMENDAR_REFUERZO` y `ABSTENERSE`. |
| Sensors | Lectura logica de `percepciones.csv`; no es un sensor conectado en tiempo real. |

## Causalidad temporal

`percepciones.csv` contiene la informacion disponible hasta la hora `h`. `resultado_h_mas_1.csv` contiene la evaluacion real de la hora siguiente y se usa solamente despues de tomar la decision. No se entrega a ninguna funcion de decision ni se utiliza para construir el estado del agente.

## `tasa_otras_simulada`

Es una proporcion sintetica y aleatoria de viajes asignada a otras empresas para el ejercicio. No permite inferir la cantidad real de taxis competidores ni una cuota de mercado real. Los datos TLC representan viajes Yellow Taxi realizados y reportados, no toda la demanda ni las solicitudes no atendidas.

## Limitaciones

X y las otras empresas son entidades ficticias. La relacion inversa entre la flota de X y la participacion externa es una hipotesis didactica. Una unidad de capacidad por taxi-hora es una simplificacion. `RECOMENDAR_REFUERZO` es un mensaje para revision humana, no una orden ni un traslado ejecutado.
