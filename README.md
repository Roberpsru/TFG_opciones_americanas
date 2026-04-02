# Valoración de opciones americanas mediante métodos numéricos

## Descripción

Proyecto que implementa y compara tres métodos numéricos para calcular el precio de una opción americana:

- **Árbol binomial** (modelo CRR de Cox, Ross y Rubinstein, 1979)
- **Diferencias finitas** (esquema Crank-Nicolson sobre la EDP de Black-Scholes)
- **Monte Carlo** (algoritmo LSM de Longstaff y Schwartz, 2001)

Las opciones americanas permiten ejercer el derecho de compra o venta en cualquier momento antes del vencimiento. Eso impide obtener su precio con fórmulas cerradas (a diferencia de las europeas, que disponen de la fórmula de Black-Scholes), por lo que es necesario recurrir a aproximaciones numéricas.

El código se ha desarrollado primero en notebooks de Jupyter para facilitar la depuración y validación de cada método, y después se ha integrado en una aplicación interactiva con Streamlit.

**Aplicación desplegada:** [https://tfg-lucia-mikel.streamlit.app](https://tfg-lucia-mikel.streamlit.app)

## Objetivo académico

El objetivo no se limita a calcular un precio. Se trata de comparar los tres métodos entre sí atendiendo a varios criterios:

- **Precisión**: ¿convergen al mismo valor? ¿Cuánta resolución necesitan?
- **Velocidad**: ¿cuánto tarda cada uno?
- **Estabilidad**: ¿los resultados oscilan mucho al cambiar parámetros numéricos?
- **Griegas**: ¿cómo de fiables son las medidas de sensibilidad que produce cada método?

## Estructura del proyecto

```
TFG_opciones_americanas/
│
├── notebooks/
│   ├── desarrollo.ipynb              # Notebook de desarrollo (put americana)
│   └── desarrollo_call.ipynb         # Notebook de desarrollo (call americana)
│
├── methods/
│   ├── __init__.py
│   ├── binomial.py                   # Árbol binomial CRR
│   ├── diferencias_finitas.py        # Diferencias finitas (Crank-Nicolson)
│   └── monte_carlo.py                # Monte Carlo (LSM)
│
├── utils/
│   ├── __init__.py
│   ├── black_scholes.py              # Fórmula de Black-Scholes (referencia europea)
│   └── griegos.py                    # Cálculo numérico de las griegas
│
├── app/
│   └── app.py                        # Aplicación interactiva en Streamlit
│
├── assets/
│   └── Logo.jpeg                     # Logo de UNIE Universidad
│
├── requirements.txt                  # Dependencias de Python
├── .gitignore
└── README.md                         # Este archivo
```

## Contenido de la aplicación

La app organiza los resultados en seis pestañas:

| Pestaña | Contenido |
|---------|-----------|
| **Comparación** | Gráficas de precios y tiempos, tabla de resultados por método, tabla comparativa método a método |
| **Binomial** | Convergencia del precio, error de convergencia, frontera de ejercicio óptimo, árbol de valores (N=5) |
| **Diferencias finitas** | Perfil de valor, evolución temporal V(S,t), frontera de ejercicio, mapa de calor V(S,t) |
| **Monte Carlo** | Trayectorias simuladas, histograma de S(T), histograma del payoff descontado, convergencia del estimador con IC 95% |
| **Griegas** | Tabla comparativa de Delta, Gamma, Theta, Vega y Rho, con gráficas de barras agrupadas |
| **Conclusiones** | Texto generado automáticamente a partir de los resultados: precios, velocidad, griegas, recomendaciones y limitaciones |

## Instalación (ejecución local)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Roberpsru/TFG_opciones_americanas.git
cd TFG_opciones_americanas
```

### 2. Crear el entorno virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

### Notebooks de desarrollo

Abrir el proyecto en Visual Studio Code y ejecutar los notebooks en `notebooks/`. Cada celda está pensada para ejecutarse en orden.

- `desarrollo.ipynb`: caso de referencia con una put americana ATM (S₀=100, K=100).
- `desarrollo_call.ipynb`: caso de referencia con una call americana ITM (S₀=110, K=100).

### Aplicación en Streamlit (local)

```bash
streamlit run app/app.py
```

Se abre una pestaña en el navegador con la interfaz interactiva.

### Aplicación desplegada

La app también está disponible en la nube, sin necesidad de instalación:

[https://tfg-lucia-mikel.streamlit.app](https://tfg-lucia-mikel.streamlit.app)

## Parámetros de entrada

| Parámetro | Símbolo | Descripción | Ejemplo |
|-----------|---------|-------------|---------|
| Precio del subyacente | S₀ | Precio actual del activo | 100 |
| Strike | K | Precio de ejercicio pactado | 100 |
| Vencimiento | T | Tiempo hasta expiración (años) | 1.0 |
| Tasa libre de riesgo | r | Tipo de interés anual continuo | 0.05 |
| Volatilidad | σ | Volatilidad anualizada del activo | 0.20 |
| Tipo de opción | — | Call (compra) o Put (venta) | put |

Cada método tiene además sus propios parámetros numéricos (número de pasos del árbol, nodos de la malla, número de trayectorias, etc.) que se pueden ajustar desde la barra lateral de la app.

## Las griegas

Las griegas son medidas de sensibilidad del precio de la opción respecto a cambios en los parámetros de mercado. Se calculan numéricamente con cada método para poder compararlos.

| Griega | Símbolo | Qué mide |
|--------|---------|----------|
| Delta | Δ | Sensibilidad al precio del subyacente (∂V/∂S) |
| Gamma | Γ | Variación de Delta al moverse el subyacente (∂²V/∂S²) |
| Theta | Θ | Pérdida de valor por el paso del tiempo (∂V/∂t) |
| Vega | ν | Sensibilidad a cambios en la volatilidad (∂V/∂σ) |
| Rho | ρ | Sensibilidad al tipo de interés (∂V/∂r) |

## Limitaciones

- Se asume volatilidad y tipo de interés constantes.
- No se consideran costes de transacción ni impuestos.
- Monte Carlo con LSM presenta un ligero sesgo a la baja por la aproximación de la regresión.
- Las griegas se aproximan por perturbaciones numéricas, lo que introduce cierto error.
- La app está pensada como herramienta didáctica, no como software de trading.

## Posibles mejoras futuras

- Incorporar dividendos discretos o continuos.
- Usar volatilidad local o estocástica.
- Añadir otros métodos (trinomial, elementos finitos).
- Comparar con precios de mercado reales.
- Optimizar el rendimiento con Numba o Cython para los bucles más pesados.

## Dependencias

- Python 3.10 o superior
- numpy
- scipy
- matplotlib
- pandas
- streamlit

Se instalan con `pip install -r requirements.txt`.

## Autores

- Lucía Carmona Cabezas
- Mikel Pérez de San Román Ruiz de Gordoa

**Tutor:** Prof. D. Guillermo Serna Calderón

Trabajo de Fin de Grado — UNIE Universidad — Curso 2025–2026