"""
Fórmula cerrada de Black-Scholes para opciones europeas.
Se usa como referencia teórica para comparar con los métodos numéricos.
"""

import numpy as np
from scipy.stats import norm


def precio_bs_europeo(S0, K, T, r, sigma, tipo='put'):
    """
    Precio de una opción europea con la fórmula de Black-Scholes.
    
    Parámetros
    ----------
    S0    : float - Precio actual del subyacente
    K     : float - Precio de ejercicio
    T     : float - Tiempo al vencimiento (años)
    r     : float - Tasa libre de riesgo
    sigma : float - Volatilidad
    tipo  : str   - 'call' o 'put'
    
    Retorna
    -------
    precio : float - Valor de la opción europea
    """
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if tipo == 'call':
        precio = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        precio = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)
    
    return precio