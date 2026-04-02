"""
Método binomial CRR (Cox, Ross, Rubinstein) para la valoración
de opciones americanas.
"""

import numpy as np


def precio_binomial(S0, K, T, r, sigma, tipo='put', N=100):
    """
    Calcula el precio de una opción americana con el modelo binomial CRR.
    
    Parámetros
    ----------
    S0    : float - Precio actual del subyacente
    K     : float - Precio de ejercicio
    T     : float - Tiempo al vencimiento (años)
    r     : float - Tasa libre de riesgo
    sigma : float - Volatilidad
    tipo  : str   - 'call' o 'put'
    N     : int   - Número de pasos del árbol
    
    Retorna
    -------
    precio : float - Valor de la opción americana
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    descuento = np.exp(-r * dt)
    
    # Precios del subyacente en el último paso (vencimiento)
    precios_final = np.array([S0 * u**(N - j) * d**j for j in range(N + 1)])
    
    # Payoff en el vencimiento
    if tipo == 'call':
        valores = np.maximum(precios_final - K, 0.0)
    else:
        valores = np.maximum(K - precios_final, 0.0)
    
    # Inducción hacia atrás
    for i in range(N - 1, -1, -1):
        precios_i = np.array([S0 * u**(i - j) * d**j for j in range(i + 1)])
        continuacion = descuento * (p * valores[:i+1] + (1 - p) * valores[1:i+2])
        
        if tipo == 'call':
            ejercicio = np.maximum(precios_i - K, 0.0)
        else:
            ejercicio = np.maximum(K - precios_i, 0.0)
        
        valores = np.maximum(continuacion, ejercicio)
    
    return float(valores[0])


def construir_arbol(S0, K, T, r, sigma, tipo='put', N=50):
    """
    Construye el árbol binomial completo y devuelve las matrices de
    precios, valores de la opción y nodos donde se ejerce anticipadamente.
    
    Parámetros
    ----------
    S0    : float - Precio actual del subyacente
    K     : float - Precio de ejercicio
    T     : float - Tiempo al vencimiento (años)
    r     : float - Tasa libre de riesgo
    sigma : float - Volatilidad
    tipo  : str   - 'call' o 'put'
    N     : int   - Número de pasos del árbol
    
    Retorna
    -------
    precio : float      - Valor de la opción americana
    S      : np.array   - Matriz (N+1 x N+1) de precios del subyacente
    V      : np.array   - Matriz (N+1 x N+1) de valores de la opción
    E      : np.array   - Matriz (N+1 x N+1) booleana, True si se ejerce anticipadamente
    u      : float      - Factor de subida
    d      : float      - Factor de bajada
    p      : float      - Probabilidad neutral al riesgo
    dt     : float      - Tamaño del paso temporal
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    descuento = np.exp(-r * dt)
    
    # Matrices para guardar todo el árbol
    S = np.zeros((N + 1, N + 1))
    V = np.zeros((N + 1, N + 1))
    E = np.zeros((N + 1, N + 1), dtype=bool)
    
    # Precios del subyacente en cada nodo
    for i in range(N + 1):
        for j in range(i + 1):
            S[j, i] = S0 * u**(i - j) * d**j
    
    # Payoff en el vencimiento
    for j in range(N + 1):
        if tipo == 'call':
            V[j, N] = max(S[j, N] - K, 0.0)
        else:
            V[j, N] = max(K - S[j, N], 0.0)
    
    # Inducción hacia atrás con detección de ejercicio anticipado
    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            continuacion = descuento * (p * V[j, i+1] + (1 - p) * V[j+1, i+1])
            
            if tipo == 'call':
                intrinseco = max(S[j, i] - K, 0.0)
            else:
                intrinseco = max(K - S[j, i], 0.0)
            
            # Si vale más ejercer que esperar, se marca como ejercicio anticipado
            if intrinseco > continuacion:
                V[j, i] = intrinseco
                E[j, i] = True
            else:
                V[j, i] = continuacion
    
    return V[0, 0], S, V, E, u, d, p, dt
