# Valoración de opciones americanas mediante métodos numéricos

## Descripción

Este proyecto implementa y compara tres métodos numéricos para calcular el precio de una opción americana:

- **Árbol binomial** (modelo CRR de Cox, Ross y Rubinstein, 1979)
- **Diferencias finitas** (esquema Crank-Nicolson sobre la EDP de Black-Scholes)
- **Monte Carlo** (algoritmo LSM de Longstaff y Schwartz, 2001)

Las opciones americanas permiten ejercer el derecho de compra o venta en cualquier momento antes del vencimiento, no solo al final. Esa flexibilidad hace que no exista una fórmula cerrada para calcular su precio (a diferencia de las europeas, que tienen la fórmula de Black-Scholes). Por eso es necesario recurrir a métodos numéricos.

El proyecto forma parte de un Trabajo de Fin de Grado. El código se ha desarrollado primero en un notebook de Jupyter para facilitar la depuración y la validación, y después se ha integrado en una aplicación interactiva con Streamlit.

## Objetivo académico

No se trata solo de calcular un precio. El objetivo es comparar los tres métodos entre sí en función de varios criterios:

- **Precisión**: ¿convergen al mismo valor? ¿Cuánta resolución necesitan?
- **Velocidad**: ¿cuánto tarda cada uno?
- **Estabilidad**: ¿los resultados oscilan mucho al cambiar parámetros numéricos?
- **Griegos**: ¿cómo de fiables son las sensibilidades que produce cada método?

## Estructura del proyecto

```
tfg_opciones_americanas/
│
├── notebooks/
│   └── desarrollo.ipynb          # Notebook de desarrollo paso a paso
│
├── methods/
│   ├── __init__.py
│   ├── binomial.py               # Método del árbol binomial (CRR)
│   ├── diferencias_finitas.py    # Método de diferencias finitas (Crank-Nicolson)
│   └── monte_carlo.py            # Método de Monte Carlo (LSM)
│
├── utils/
│   ├── __init__.py
│   ├── griegos.py                # Cálculo numérico de las griegas
│   ├── benchmark.py              # Medición de tiempos de ejecución
│   └── graficas.py               # Funciones de visualización
│
├── app/
│   └── app.py                    # Aplicación interactiva en Streamlit
│
├── requirements.txt              # Dependencias de Python
└── README.md                     # Este archivo
```

## Instalación

### 1. Clonar o descargar el proyecto

Si se tiene acceso al repositorio:

```bash
git clone <url-del-repositorio>
cd tfg_opciones_americanas
```

Si se ha descargado como ZIP, extraerlo y entrar en la carpeta:

```bash
cd tfg_opciones_americanas
```

### 2. Crear el entorno virtual

Es recomendable trabajar en un entorno virtual para no mezclar dependencias con otros proyectos del sistema.

**En Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**En Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**En macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno esté activado, debería aparecer `(venv)` al principio de la línea del terminal.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

### Notebook de desarrollo

Abrir el proyecto en Visual Studio Code y ejecutar el notebook `notebooks/desarrollo.ipynb`. Cada celda está pensada para ejecutarse en orden; los resultados parciales se van mostrando sobre la marcha.

```bash
# Alternativa desde el terminal (si Jupyter está instalado):
jupyter notebook notebooks/desarrollo.ipynb
```

### Aplicación en Streamlit

Una vez validado todo en el notebook, la app se lanza así:

```bash
streamlit run app/app.py
```

Se abrirá una pestaña en el navegador con la interfaz interactiva.

## Parámetros de entrada

La calculadora (tanto en el notebook como en la app) trabaja con estos parámetros:

| Parámetro | Símbolo | Descripción | Ejemplo |
|-----------|---------|-------------|---------|
| Precio del subyacente | S₀ | Precio actual del activo | 100 |
| Strike | K | Precio de ejercicio pactado | 100 |
| Vencimiento | T | Tiempo hasta expiración (años) | 1.0 |
| Tasa libre de riesgo | r | Tipo de interés anual continuo | 0.05 |
| Volatilidad | σ | Volatilidad anualizada del activo | 0.20 |
| Tipo de opción | — | Call (compra) o Put (venta) | put |

Además, cada método tiene sus propios parámetros numéricos (número de pasos, número de simulaciones, tamaño de la malla, etc.).

## Los griegos

Los griegos (o griegas) son medidas de sensibilidad del precio de la opción respecto a cambios en los parámetros de mercado. Se calculan numéricamente con cada método para poder compararlos.

| Griego | Símbolo | Qué mide |
|--------|---------|----------|
| Delta | Δ | Sensibilidad al precio del subyacente (∂V/∂S) |
| Gamma | Γ | Variación de Delta al moverse el subyacente (∂²V/∂S²) |
| Theta | Θ | Pérdida de valor por el paso del tiempo (∂V/∂t) |
| Vega | ν | Sensibilidad a cambios en la volatilidad (∂V/∂σ) |
| Rho | ρ | Sensibilidad al tipo de interés (∂V/∂r) |

## Limitaciones

- El modelo asume volatilidad y tipo de interés constantes, cosa que no ocurre en mercados reales.
- No se consideran dividendos (se podría ampliar).
- Monte Carlo con LSM puede dar resultados ligeramente distintos en cada ejecución por su naturaleza aleatoria.
- Las griegas se aproximan por diferencias finitas numéricas, lo cual introduce cierto error.
- La app de Streamlit está pensada como herramienta didáctica, no como software de trading.

## Posibles mejoras futuras

- Incorporar dividendos discretos o continuos.
- Usar volatilidad local o estocástica en lugar de constante.
- Añadir más métodos (trinomial, método de elementos finitos).
- Comparar con precios de mercado reales.
- Optimizar el rendimiento con Cython o Numba para los bucles más pesados.

## Dependencias

- Python 3.10 o superior
- numpy
- scipy
- matplotlib
- pandas
- streamlit

Todas se instalan con `pip install -r requirements.txt`.

## Autores

- Lucía Carmona Cabezas
- Mikel Pérez de San Román Ruiz de Gordoa

**Tutor:** Prof. D. Guillermo Serna Calderón

Trabajo de Fin de Grado — Curso 2025–2026
