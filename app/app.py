"""
Calculadora de opciones americanas — Comparación de métodos numéricos
Aplicación interactiva en Streamlit.

Ejecutar desde la raíz del proyecto:
    streamlit run app/app.py
"""

import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Añadir la raíz del proyecto al path para poder importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from methods.binomial import precio_binomial
from methods.diferencias_finitas import precio_diferencias_finitas
from methods.monte_carlo import precio_monte_carlo
from utils.black_scholes import precio_bs_europeo
from utils.griegos import calcular_griegos


# ============================================================
# Configuración de la página
# ============================================================

st.set_page_config(
    page_title="Opciones Americanas — TFG",
    page_icon="📊",
    layout="wide",
)

st.title("Valoración de opciones americanas")
st.markdown("Comparación de tres métodos numéricos: **Binomial**, **Diferencias Finitas** y **Monte Carlo (LSM)**")
st.divider()


# ============================================================
# Barra lateral: parámetros de entrada
# ============================================================

st.sidebar.header("Parámetros de la opción")

S0 = st.sidebar.number_input("S₀ — Precio del subyacente", min_value=1.0, max_value=500.0, value=100.0, step=1.0)
K = st.sidebar.number_input("K — Strike (precio de ejercicio)", min_value=1.0, max_value=500.0, value=100.0, step=1.0)
T = st.sidebar.number_input("T — Tiempo al vencimiento (años)", min_value=0.05, max_value=5.0, value=1.0, step=0.05)
sigma = st.sidebar.number_input("σ — Volatilidad", min_value=0.01, max_value=1.50, value=0.20, step=0.01, format="%.2f")
r = st.sidebar.number_input("r — Tasa libre de riesgo", min_value=0.00, max_value=0.30, value=0.05, step=0.005, format="%.3f")
tipo = st.sidebar.selectbox("Tipo de opción", ["put", "call"])

st.sidebar.divider()
st.sidebar.header("Parámetros numéricos")

N_bin = st.sidebar.slider("Binomial — Pasos (N)", min_value=10, max_value=500, value=200, step=10)
N_S_fd = st.sidebar.slider("Dif. finitas — Nodos espaciales (N_S)", min_value=50, max_value=400, value=200, step=50)
N_T_fd = st.sidebar.slider("Dif. finitas — Pasos temporales (N_T)", min_value=200, max_value=2000, value=800, step=100)
M_mc = st.sidebar.slider("Monte Carlo — Trayectorias (M)", min_value=5000, max_value=200000, value=50000, step=5000)
N_mc = st.sidebar.slider("Monte Carlo — Pasos temporales (N)", min_value=50, max_value=200, value=100, step=10)

st.sidebar.divider()
calcular = st.sidebar.button("▶  Calcular", type="primary", use_container_width=True)


# ============================================================
# Cálculos
# ============================================================

if calcular:
    # Precio europeo de referencia
    p_eu = precio_bs_europeo(S0, K, T, r, sigma, tipo)

    # --- Binomial ---
    t0 = time.perf_counter()
    p_bin = precio_binomial(S0, K, T, r, sigma, tipo, N=N_bin)
    t_bin = (time.perf_counter() - t0) * 1000

    # --- Diferencias finitas ---
    t0 = time.perf_counter()
    p_fd, S_grid, V_grid = precio_diferencias_finitas(S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd)
    t_fd = (time.perf_counter() - t0) * 1000

    # --- Monte Carlo ---
    t0 = time.perf_counter()
    p_mc, trayectorias = precio_monte_carlo(S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc)
    t_mc = (time.perf_counter() - t0) * 1000

    # Estado de la opción
    if S0 == K:
        estado = "ATM"
    elif (tipo == 'put' and S0 < K) or (tipo == 'call' and S0 > K):
        estado = "ITM"
    else:
        estado = "OTM"

    # ============================================================
    # Resultados principales
    # ============================================================

    st.header("Resultados")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Binomial", f"{p_bin:.4f}", f"{t_bin:.1f} ms")
    col2.metric("Dif. finitas", f"{p_fd:.4f}", f"{t_fd:.1f} ms")
    col3.metric("Monte Carlo", f"{p_mc:.4f}", f"{t_mc:.1f} ms")
    col4.metric("Europea (B-S)", f"{p_eu:.4f}", f"ref.")

    st.caption(f"Tipo: **{tipo.upper()}** | Estado: **{estado}** | Prima de ejercicio anticipado: **{p_bin - p_eu:.4f}**")
    st.divider()

    # ============================================================
    # Pestañas de visualización
    # ============================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Comparación",
        "🌳 Binomial",
        "📐 Diferencias finitas",
        "🎲 Monte Carlo",
        "📈 Griegos",
    ])

    # --- Tab 1: Comparación de precios y tiempos ---
    with tab1:
        st.subheader("Comparación de precios y tiempos")

        col_a, col_b = st.columns(2)

        with col_a:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            metodos = ['Binomial', 'Dif. finitas', 'Monte Carlo']
            precios = [p_bin, p_fd, p_mc]
            colores = ['steelblue', 'seagreen', 'indianred']
            ax1.bar(metodos, precios, color=colores, alpha=0.8)
            ax1.axhline(p_eu, color='gray', linestyle='--', linewidth=1.0, label=f'Europea = {p_eu:.4f}')
            ax1.set_ylabel('Precio')
            ax1.set_title('Precios de la opción')
            ax1.legend(fontsize=9)
            ax1.set_ylim(p_eu * 0.95, max(precios) * 1.02)
            st.pyplot(fig1)
            plt.close()

        with col_b:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            tiempos = [t_bin, t_fd, t_mc]
            ax2.bar(metodos, tiempos, color=colores, alpha=0.8)
            ax2.set_ylabel('Tiempo (ms)')
            ax2.set_title('Tiempos de ejecución')
            st.pyplot(fig2)
            plt.close()

        # Tabla resumen
        st.subheader("Tabla resumen")
        st.markdown(f"""
        | Método | Precio | Tiempo | Dif. vs binomial |
        |--------|--------|--------|-----------------|
        | Binomial (N={N_bin}) | {p_bin:.6f} | {t_bin:.1f} ms | (ref.) |
        | Dif. finitas ({N_S_fd}x{N_T_fd}) | {p_fd:.6f} | {t_fd:.1f} ms | {abs(p_fd-p_bin):.6f} |
        | Monte Carlo (M={M_mc//1000}K) | {p_mc:.6f} | {t_mc:.1f} ms | {abs(p_mc-p_bin):.6f} |
        | Europea (B-S) | {p_eu:.6f} | — | — |
        """)

    # --- Tab 2: Binomial ---
    with tab2:
        st.subheader("Convergencia del método binomial")

        valores_N = list(range(5, 305, 5))
        precios_conv = [precio_binomial(S0, K, T, r, sigma, tipo, n) for n in valores_N]

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.plot(valores_N, precios_conv, color='steelblue', linewidth=1.2, label='Americana (binomial)')
        ax3.axhline(p_eu, color='darkorange', linestyle='--', linewidth=1.0, label=f'Europea (B-S) = {p_eu:.4f}')
        ax3.set_xlabel('Número de pasos (N)')
        ax3.set_ylabel('Precio')
        ax3.set_title('Convergencia del método binomial')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)
        plt.close()

    # --- Tab 3: Diferencias finitas ---
    with tab3:
        st.subheader("Perfil de valor — Diferencias finitas")

        if tipo == 'call':
            intrinseco = np.maximum(S_grid - K, 0.0)
        else:
            intrinseco = np.maximum(K - S_grid, 0.0)

        mascara = (S_grid >= K * 0.3) & (S_grid <= K * 2.0)

        fig4, ax4 = plt.subplots(figsize=(10, 5))
        ax4.plot(S_grid[mascara], V_grid[mascara], color='steelblue', linewidth=2.0,
                 label=f'{tipo.upper()} americana')
        ax4.plot(S_grid[mascara], intrinseco[mascara], color='gray', linewidth=1.0,
                 linestyle='--', label='Valor intrínseco')
        ax4.axvline(S0, color='goldenrod', linewidth=1.2, linestyle=':', label=f'S₀ = {S0}')
        ax4.axvline(K, color='silver', linewidth=0.8, linestyle=':', label=f'K = {K}')
        ax4.set_xlabel('Precio del subyacente (S)')
        ax4.set_ylabel('Valor de la opción V(S)')
        ax4.set_title('Perfil de valor — Diferencias finitas (Crank-Nicolson)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        st.pyplot(fig4)
        plt.close()

    # --- Tab 4: Monte Carlo ---
    with tab4:
        st.subheader("Trayectorias simuladas — Monte Carlo")

        pasos_t = np.linspace(0, T, trayectorias.shape[1])
        np.random.seed(0)
        idx_muestra = np.random.choice(trayectorias.shape[0], size=50, replace=False)

        fig5, ax5 = plt.subplots(figsize=(10, 5))
        for i in idx_muestra:
            ax5.plot(pasos_t, trayectorias[i, :], linewidth=0.5, alpha=0.5)
        ax5.axhline(K, color='firebrick', linewidth=1.2, linestyle='--', label=f'Strike K = {K}')
        ax5.axhline(S0, color='goldenrod', linewidth=1.0, linestyle=':', label=f'S₀ = {S0}')
        ax5.set_xlabel('Tiempo (años)')
        ax5.set_ylabel('Precio del subyacente (S)')
        ax5.set_title('Trayectorias simuladas — Monte Carlo')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        st.pyplot(fig5)
        plt.close()

        st.caption(f"Se muestran 50 de las {M_mc} trayectorias simuladas.")

    # --- Tab 5: Griegos ---
    with tab5:
        st.subheader("Comparación de griegos")

        with st.spinner("Calculando griegos (puede tardar unos segundos)..."):
            g_bin = calcular_griegos(precio_binomial, S0, K, T, r, sigma, tipo, N=N_bin)

            def _precio_fd(S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd):
                return precio_diferencias_finitas(S0, K, T, r, sigma, tipo, N_S, N_T)

            def _precio_mc(S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc):
                return precio_monte_carlo(S0, K, T, r, sigma, tipo, M, N)

            g_fd = calcular_griegos(_precio_fd, S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd)
            g_mc = calcular_griegos(_precio_mc, S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc)

        # Tabla de griegos
        st.markdown(f"""
        | Griego | Binomial | Dif. finitas | Monte Carlo |
        |--------|----------|-------------|-------------|
        | Delta (Δ) | {g_bin['Delta']:+.6f} | {g_fd['Delta']:+.6f} | {g_mc['Delta']:+.6f} |
        | Gamma (Γ) | {g_bin['Gamma']:+.6f} | {g_fd['Gamma']:+.6f} | {g_mc['Gamma']:+.6f} |
        | Theta (Θ) | {g_bin['Theta']:+.6f} | {g_fd['Theta']:+.6f} | {g_mc['Theta']:+.6f} |
        | Vega (ν) | {g_bin['Vega']:+.4f} | {g_fd['Vega']:+.4f} | {g_mc['Vega']:+.4f} |
        | Rho (ρ) | {g_bin['Rho']:+.4f} | {g_fd['Rho']:+.4f} | {g_mc['Rho']:+.4f} |
        """)

        # Gráfica de griegos
        griegos_peq = ['Delta', 'Gamma', 'Theta']
        griegos_gra = ['Vega', 'Rho']

        fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(13, 5))

        x = np.arange(len(griegos_peq))
        ancho = 0.25

        ax6a.bar(x - ancho, [g_bin[g] for g in griegos_peq], ancho, color='steelblue', alpha=0.8, label='Binomial')
        ax6a.bar(x,         [g_fd[g] for g in griegos_peq],  ancho, color='seagreen',  alpha=0.8, label='Dif. finitas')
        ax6a.bar(x + ancho, [g_mc[g] for g in griegos_peq],  ancho, color='indianred',  alpha=0.8, label='Monte Carlo')
        ax6a.set_xticks(x)
        ax6a.set_xticklabels(griegos_peq)
        ax6a.set_title('Delta, Gamma y Theta')
        ax6a.legend(fontsize=9)
        ax6a.axhline(0, color='gray', linewidth=0.5)
        ax6a.grid(True, alpha=0.3)

        x2 = np.arange(len(griegos_gra))

        ax6b.bar(x2 - ancho, [g_bin[g] for g in griegos_gra], ancho, color='steelblue', alpha=0.8, label='Binomial')
        ax6b.bar(x2,         [g_fd[g] for g in griegos_gra],  ancho, color='seagreen',  alpha=0.8, label='Dif. finitas')
        ax6b.bar(x2 + ancho, [g_mc[g] for g in griegos_gra],  ancho, color='indianred',  alpha=0.8, label='Monte Carlo')
        ax6b.set_xticks(x2)
        ax6b.set_xticklabels(griegos_gra)
        ax6b.set_title('Vega y Rho')
        ax6b.legend(fontsize=9)
        ax6b.axhline(0, color='gray', linewidth=0.5)
        ax6b.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

else:
    st.info("Ajusta los parámetros en la barra lateral y pulsa **Calcular** para ver los resultados.")