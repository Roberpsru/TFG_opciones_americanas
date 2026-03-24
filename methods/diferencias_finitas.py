"""
Método de diferencias finitas (Crank-Nicolson) para la valoración
de opciones americanas. Resuelve la EDP de Black-Scholes sobre
una malla de precios y tiempos.
"""

import numpy as np
from scipy import linalg


def precio_diferencias_finitas(S0, K, T, r, sigma, tipo='put', N_S=200, N_T=1000):
    """
    Calcula el precio de una opción americana mediante diferencias finitas
    con el esquema Crank-Nicolson.
    
    Parámetros
    ----------
    S0    : float - Precio actual del subyacente
    K     : float - Precio de ejercicio
    T     : float - Tiempo al vencimiento (años)
    r     : float - Tasa libre de riesgo
    sigma : float - Volatilidad
    tipo  : str   - 'call' o 'put'
    N_S   : int   - Número de nodos en la dimensión del precio
    N_T   : int   - Número de pasos temporales
    
    Retorna
    -------
    precio  : float    - Valor de la opción americana en S0
    S_grid  : np.array - Vector de precios del subyacente (malla)
    V_grid  : np.array - Vector de valores de la opción en t=0
    """
    S_max = 4.0 * K
    dS = S_max / N_S
    S = np.linspace(0, S_max, N_S + 1)
    dt = T / N_T
    
    # Condición terminal: payoff en el vencimiento
    if tipo == 'call':
        V = np.maximum(S - K, 0.0)
    else:
        V = np.maximum(K - S, 0.0)
    
    # Índices de los nodos interiores
    idx = np.arange(1, N_S)
    
    # Coeficientes del esquema Crank-Nicolson
    alpha = 0.5 * dt * (sigma**2 * idx**2 - r * idx)
    beta  = -dt * (sigma**2 * idx**2 + r)
    gamma = 0.5 * dt * (sigma**2 * idx**2 + r * idx)
    
    theta = 0.5
    M = N_S - 1
    
    # Matriz izquierda
    diag_izq  = 1.0 - theta * beta
    sub_izq   = -theta * alpha[1:]
    super_izq = -theta * gamma[:-1]
    
    A_izq = (np.diag(diag_izq) +
             np.diag(sub_izq, -1) +
             np.diag(super_izq, 1))
    
    # Matriz derecha
    diag_der  = 1.0 + (1 - theta) * beta
    sub_der   = (1 - theta) * alpha[1:]
    super_der = (1 - theta) * gamma[:-1]
    
    A_der = (np.diag(diag_der) +
             np.diag(sub_der, -1) +
             np.diag(super_der, 1))
    
    # Factorización LU (una sola vez)
    lu, piv = linalg.lu_factor(A_izq)
    
    # Iteración hacia atrás en el tiempo
    for n in range(N_T):
        rhs = A_der @ V[1:N_S]
        
        if tipo == 'call':
            bc_izq = 0.0
            bc_der = S_max - K * np.exp(-r * (T - (n + 1) * dt))
        else:
            bc_izq = K * np.exp(-r * (T - (n + 1) * dt))
            bc_der = 0.0
        
        rhs[0]  += theta * alpha[0] * bc_izq + (1 - theta) * alpha[0] * V[0]
        rhs[-1] += theta * gamma[-1] * bc_der + (1 - theta) * gamma[-1] * V[N_S]
        
        V_nuevo = linalg.lu_solve((lu, piv), rhs)
        
        if tipo == 'call':
            intrinseco = np.maximum(S[1:N_S] - K, 0.0)
        else:
            intrinseco = np.maximum(K - S[1:N_S], 0.0)
        
        V_nuevo = np.maximum(V_nuevo, intrinseco)
        
        V[0]      = bc_izq
        V[N_S]    = bc_der
        V[1:N_S]  = V_nuevo
    
    precio = np.interp(S0, S, V)
    
    return precio, S, V