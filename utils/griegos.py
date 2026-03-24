"""
Cálculo numérico de los griegos (sensibilidades) para cualquier
método de valoración de opciones americanas.
"""


def calcular_griegos(funcion_precio, S0, K, T, r, sigma, tipo, **kwargs):
    """
    Calcula los cinco griegos de forma numérica. Se perturba cada
    parámetro ligeramente y se estima la derivada por diferencias
    centrales (o hacia adelante en algunos casos).
    
    Parámetros
    ----------
    funcion_precio : callable - Función que devuelve el precio
    S0, K, T, r, sigma, tipo : parámetros de la opción
    **kwargs : parámetros adicionales del método (N, N_S, N_T, M, etc.)
    
    Retorna
    -------
    dict con Delta, Gamma, Theta, Vega, Rho
    """
    # Extraer solo el precio (algunas funciones devuelven tuplas)
    def precio(S0_, K_, T_, r_, sigma_, tipo_):
        resultado = funcion_precio(S0_, K_, T_, r_, sigma_, tipo_, **kwargs)
        if isinstance(resultado, tuple):
            return resultado[0]
        return resultado
    
    # Perturbaciones
    h_S = S0 * 0.01
    h_sigma = 0.001
    h_r = 0.0001
    h_T = max(T * 0.01, 1e-4)
    
    # Precio base
    p0 = precio(S0, K, T, r, sigma, tipo)
    
    # Delta = dV/dS
    p_up_S = precio(S0 + h_S, K, T, r, sigma, tipo)
    p_dn_S = precio(S0 - h_S, K, T, r, sigma, tipo)
    delta = (p_up_S - p_dn_S) / (2 * h_S)
    
    # Gamma = d²V/dS²
    gamma = (p_up_S - 2 * p0 + p_dn_S) / (h_S ** 2)
    
    # Theta = dV/dt (por día)
    p_menos_T = precio(S0, K, T - h_T, r, sigma, tipo)
    theta = -(p_menos_T - p0) / h_T / 365
    
    # Vega = dV/dsigma
    p_up_sigma = precio(S0, K, T, r, sigma + h_sigma, tipo)
    vega = (p_up_sigma - p0) / h_sigma
    
    # Rho = dV/dr
    p_up_r = precio(S0, K, T, r + h_r, sigma, tipo)
    rho = (p_up_r - p0) / h_r
    
    return {
        'Delta': delta,
        'Gamma': gamma,
        'Theta': theta,
        'Vega':  vega,
        'Rho':   rho,
    }