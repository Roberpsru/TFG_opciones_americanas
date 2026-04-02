"""
Método de Monte Carlo con el algoritmo LSM (Longstaff-Schwartz)
para la valoración de opciones americanas.
"""
 
import numpy as np
 
 
def precio_monte_carlo(S0, K, T, r, sigma, tipo='put', M=50000, N=100, semilla=42):
    """
    Calcula el precio de una opción americana mediante simulación de
    Monte Carlo con el algoritmo LSM (Longstaff-Schwartz).
    
    Parámetros
    ----------
    S0     : float - Precio actual del subyacente
    K      : float - Precio de ejercicio
    T      : float - Tiempo al vencimiento (años)
    r      : float - Tasa libre de riesgo
    sigma  : float - Volatilidad
    tipo   : str   - 'call' o 'put'
    M      : int   - Número de trayectorias simuladas
    N      : int   - Número de pasos temporales
    semilla: int   - Semilla aleatoria (para reproducibilidad)
    
    Retorna
    -------
    precio       : float    - Valor de la opción americana
    trayectorias : np.array - Matriz de trayectorias (M x N+1)
    """
    np.random.seed(semilla)
    dt = T / N
    descuento = np.exp(-r * dt)
    
    Z = np.random.standard_normal((M, N))
    S = np.zeros((M, N + 1))
    S[:, 0] = S0
    
    for t in range(1, N + 1):
        S[:, t] = S[:, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, t-1])
    
    if tipo == 'call':
        payoff = np.maximum(S - K, 0.0)
    else:
        payoff = np.maximum(K - S, 0.0)
    
    flujo_caja = payoff[:, -1].copy()
    momento_ejercicio = np.full(M, N)
    
    for t in range(N - 1, 0, -1):
        itm = payoff[:, t] > 0
        
        if np.sum(itm) == 0:
            continue
        
        S_itm = S[itm, t]
        
        pasos_hasta_ejercicio = momento_ejercicio[itm] - t
        flujo_futuro = payoff[itm, momento_ejercicio[itm]] * descuento ** pasos_hasta_ejercicio
        
        X = np.column_stack([np.ones_like(S_itm), S_itm, S_itm**2])
        coef, _, _, _ = np.linalg.lstsq(X, flujo_futuro, rcond=None)
        valor_continuacion = X @ coef
        
        ejercer_ahora = payoff[itm, t] >= valor_continuacion
        
        indices_itm = np.where(itm)[0]
        indices_ejercer = indices_itm[ejercer_ahora]
        
        flujo_caja[indices_ejercer] = payoff[indices_ejercer, t]
        momento_ejercicio[indices_ejercer] = t
    
    flujos_descontados = flujo_caja * descuento ** momento_ejercicio
    precio = float(np.mean(flujos_descontados))
    
    return precio, S
 
 
def precio_monte_carlo_detallado(S0, K, T, r, sigma, tipo='put', M=50000, N=100, semilla=42):
    """
    Igual que precio_monte_carlo, pero devuelve información adicional
    para las visualizaciones: flujos descontados por trayectoria y
    momento de ejercicio.
    
    Parámetros
    ----------
    (mismos que precio_monte_carlo)
    
    Retorna
    -------
    precio              : float    - Valor de la opción americana
    trayectorias        : np.array - Matriz de trayectorias (M x N+1)
    flujos_descontados  : np.array - Flujo descontado óptimo de cada trayectoria (M,)
    momento_ejercicio   : np.array - Paso en el que se ejerce cada trayectoria (M,)
    """
    np.random.seed(semilla)
    dt = T / N
    descuento = np.exp(-r * dt)
    
    Z = np.random.standard_normal((M, N))
    S = np.zeros((M, N + 1))
    S[:, 0] = S0
    
    for t in range(1, N + 1):
        S[:, t] = S[:, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, t-1])
    
    if tipo == 'call':
        payoff = np.maximum(S - K, 0.0)
    else:
        payoff = np.maximum(K - S, 0.0)
    
    flujo_caja = payoff[:, -1].copy()
    momento_ejercicio = np.full(M, N)
    
    for t in range(N - 1, 0, -1):
        itm = payoff[:, t] > 0
        
        if np.sum(itm) == 0:
            continue
        
        S_itm = S[itm, t]
        
        pasos_hasta_ejercicio = momento_ejercicio[itm] - t
        flujo_futuro = payoff[itm, momento_ejercicio[itm]] * descuento ** pasos_hasta_ejercicio
        
        X = np.column_stack([np.ones_like(S_itm), S_itm, S_itm**2])
        coef, _, _, _ = np.linalg.lstsq(X, flujo_futuro, rcond=None)
        valor_continuacion = X @ coef
        
        ejercer_ahora = payoff[itm, t] >= valor_continuacion
        
        indices_itm = np.where(itm)[0]
        indices_ejercer = indices_itm[ejercer_ahora]
        
        flujo_caja[indices_ejercer] = payoff[indices_ejercer, t]
        momento_ejercicio[indices_ejercer] = t
    
    flujos_descontados = flujo_caja * descuento ** momento_ejercicio
    precio = float(np.mean(flujos_descontados))
    
    return precio, S, flujos_descontados, momento_ejercicio
 