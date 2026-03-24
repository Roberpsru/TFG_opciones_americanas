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