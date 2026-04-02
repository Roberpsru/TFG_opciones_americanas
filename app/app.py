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
 
from methods.binomial import precio_binomial, construir_arbol
from methods.diferencias_finitas import precio_diferencias_finitas, resolver_malla_completa
from methods.monte_carlo import precio_monte_carlo, precio_monte_carlo_detallado
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
 
st.markdown(
    """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p,
    button[data-baseweb="tab"] > div > p,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"],
    [role="tab"],
    [role="tab"] p {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
    }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(1),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(1) p { color: #2c3e50 !important; }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(2),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(2) p { color: steelblue !important; }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(3),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(3) p { color: seagreen !important; }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(4),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(4) p { color: indianred !important; }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(5),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(5) p { color: #8e44ad !important; }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(6),
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:nth-child(6) p { color: #e67e22 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2c3e50 !important; height: 3px !important; }
 
    /* Ocultar todos los elementos de Streamlit */
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important; display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__r5tak {display: none !important;}
    .stApp [data-testid="stHeader"] {display: none !important;}
    iframe[title="streamlit_badgeST"] {display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    .reportview-container .main footer {visibility: hidden !important;}
    #stStreamlitBadge {display: none !important;}
    ._profileContainer_gzau3_53 {display: none !important;}
    ._container_gzau3_1 {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)
 
ruta_logo = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Logo.jpeg')
 
# ============================================================
# Barra lateral
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
 
if calcular:
    st.session_state['calculado'] = True
ya_calculado = st.session_state.get('calculado', False)
 
# ============================================================
# Cabecera
# ============================================================
 
if not ya_calculado:
    col_logo, col_info = st.columns([1, 2])
    with col_logo:
        st.image(ruta_logo, width=220)
    with col_info:
        st.markdown(
            """
            <div style='padding-top: 5px;'>
            <h3 style='margin-bottom: 2px; color: #1a5276;'>Trabajo Final de Grado (TFG)</h3>
            <span style='font-size: 0.88em;'><b>Alumnos:</b> Lucía Carmona Cabezas · Mikel Pérez de San Román Ruiz de Gordoa</span><br>
            <span style='font-size: 0.88em;'><b>Tutor:</b> Prof. D. Guillermo Serna Calderón</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<h1 style='color: #2c3e50; margin-top: 10px; margin-bottom: 0px;'>Valoración de opciones americanas</h1>", unsafe_allow_html=True)
    st.markdown(
        "<span style='font-size: 1.05em;'>Comparación de tres métodos numéricos: "
        "<b style='color: steelblue;'>Binomial</b>, "
        "<b style='color: seagreen;'>Diferencias Finitas</b> y "
        "<b style='color: indianred;'>Monte Carlo (LSM)</b></span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style='font-size: 0.92em; color: #555; margin-top: 8px; margin-bottom: 5px;'>
        Las opciones americanas permiten ejercer el derecho de compra o venta en cualquier momento
        antes del vencimiento, lo que impide obtener su precio mediante fórmulas cerradas. Esta
        aplicación implementa tres métodos numéricos para aproximar dicho precio y permite compararlos
        en términos de convergencia, velocidad y estabilidad bajo distintos escenarios de mercado.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.info("Ajusta los parámetros en la barra lateral y pulsa **Calcular** para ver los resultados.")
else:
    col_mini_logo, col_mini_titulo = st.columns([1, 8])
    with col_mini_logo:
        st.image(ruta_logo, width=80)
    with col_mini_titulo:
        st.markdown("<h2 style='color: #2c3e50; margin-top: 12px; margin-bottom: 0px;'>Valoración de opciones americanas</h2>", unsafe_allow_html=True)
    st.divider()
 
# ============================================================
# Cálculos
# ============================================================
 
if calcular:
    p_eu = precio_bs_europeo(S0, K, T, r, sigma, tipo)
 
    t0 = time.perf_counter()
    p_bin = precio_binomial(S0, K, T, r, sigma, tipo, N=N_bin)
    t_bin = (time.perf_counter() - t0) * 1000
 
    t0 = time.perf_counter()
    p_fd, S_grid, V_grid = precio_diferencias_finitas(S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd)
    t_fd = (time.perf_counter() - t0) * 1000
 
    t0 = time.perf_counter()
    p_mc, trayectorias, flujos_desc, momento_ej = precio_monte_carlo_detallado(
        S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc
    )
    t_mc = (time.perf_counter() - t0) * 1000
 
    if S0 == K:
        estado = "ATM"
    elif (tipo == 'put' and S0 < K) or (tipo == 'call' and S0 > K):
        estado = "ITM"
    else:
        estado = "OTM"
 
    # Calcular griegas
    with st.spinner("Calculando griegas..."):
        g_bin = calcular_griegos(precio_binomial, S0, K, T, r, sigma, tipo, N=N_bin)
 
        def _precio_fd(S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd):
            return precio_diferencias_finitas(S0, K, T, r, sigma, tipo, N_S, N_T)
        def _precio_mc(S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc):
            return precio_monte_carlo(S0, K, T, r, sigma, tipo, M, N)
 
        g_fd = calcular_griegos(_precio_fd, S0, K, T, r, sigma, tipo, N_S=N_S_fd, N_T=N_T_fd)
        g_mc = calcular_griegos(_precio_mc, S0, K, T, r, sigma, tipo, M=M_mc, N=N_mc)
 
    # ============================================================
    # Resultados principales
    # ============================================================
 
    st.markdown("<h3 style='color: #1a5276;'>Resultados</h3>", unsafe_allow_html=True)
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Binomial", f"{p_bin:.4f}", f"{t_bin:.1f} ms")
    col2.metric("Dif. finitas", f"{p_fd:.4f}", f"{t_fd:.1f} ms")
    col3.metric("Monte Carlo", f"{p_mc:.4f}", f"{t_mc:.1f} ms")
    col4.metric("Europea (B-S)", f"{p_eu:.4f}", f"ref.")
 
    st.caption(f"Tipo: **{tipo.upper()}** | Estado: **{estado}** | Prima de ejercicio anticipado: **{p_bin - p_eu:.4f}**")
    st.divider()
 
    # ============================================================
    # Pestañas
    # ============================================================
 
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Comparación", "Binomial", "Diferencias finitas", "Monte Carlo", "Griegas", "Conclusiones",
    ])
 
    # --- Tab 1: Comparación ---
    with tab1:
        st.subheader("Comparación de precios y tiempos")
        col_a, col_b = st.columns(2)
        with col_a:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            metodos = ['Binomial', 'Dif. finitas', 'Monte Carlo']
            precios = [p_bin, p_fd, p_mc]
            colores_met = ['steelblue', 'seagreen', 'indianred']
            ax1.bar(metodos, precios, color=colores_met, alpha=0.8)
            ax1.axhline(p_eu, color='gray', linestyle='--', linewidth=1.0, label=f'Europea = {p_eu:.4f}')
            ax1.set_ylabel('Precio')
            ax1.set_title('Precios de la opción')
            ax1.legend(fontsize=9)
            ax1.set_ylim(p_eu * 0.95, max(precios) * 1.02)
            st.pyplot(fig1)
            plt.close()
        with col_b:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            tiempos_lista = [t_bin, t_fd, t_mc]
            ax2.bar(metodos, tiempos_lista, color=colores_met, alpha=0.8)
            ax2.set_ylabel('Tiempo (ms)')
            ax2.set_title('Tiempos de ejecución')
            st.pyplot(fig2)
            plt.close()
 
        st.subheader("Resultados por método")
        st.markdown(f"""
        | Método | Precio | Tiempo |
        |--------|--------|--------|
        | Binomial (N={N_bin}) | {p_bin:.6f} | {t_bin:.1f} ms |
        | Dif. finitas ({N_S_fd}x{N_T_fd}) | {p_fd:.6f} | {t_fd:.1f} ms |
        | Monte Carlo (M={M_mc//1000}K) | {p_mc:.6f} | {t_mc:.1f} ms |
        | Europea (B-S) | {p_eu:.6f} | — |
        """)
 
        st.subheader("Comparación entre métodos")
        st.markdown(f"""
        | Comparación | Dif. precio | Dif. tiempo |
        |-------------|------------|-------------|
        | Binomial vs Dif. finitas | {p_bin - p_fd:+.6f} | {t_bin - t_fd:+.1f} ms |
        | Binomial vs Monte Carlo | {p_bin - p_mc:+.6f} | {t_bin - t_mc:+.1f} ms |
        | Dif. finitas vs Monte Carlo | {p_fd - p_mc:+.6f} | {t_fd - t_mc:+.1f} ms |
        """)
        st.caption("Diferencia positiva en precio: el primer método da un valor mayor. "
                   "Diferencia negativa en tiempo: el primer método es más rápido.")
 
    # --- Tab 2: Binomial ---
    with tab2:
        st.subheader("Convergencia del precio")
        valores_N = list(range(5, 305, 5))
        precios_conv = [precio_binomial(S0, K, T, r, sigma, tipo, n) for n in valores_N]
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.plot(valores_N, precios_conv, color='steelblue', linewidth=1.2, label='Americana (binomial)')
        ax3.axhline(p_eu, color='darkorange', linestyle='--', linewidth=1.0, label=f'Europea (B-S) = {p_eu:.4f}')
        ax3.set_xlabel('Número de pasos (N)')
        ax3.set_ylabel('Precio')
        ax3.set_title('Convergencia del método binomial')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)
        plt.close()
 
        st.divider()
        st.subheader("Error de convergencia")
        p_ref = precio_binomial(S0, K, T, r, sigma, tipo, N=500)
        errores = [abs(p - p_ref) for p in precios_conv]
        fig_err, ax_err = plt.subplots(figsize=(10, 4))
        ax_err.plot(valores_N, errores, color='steelblue', linewidth=1.2)
        ax_err.scatter(valores_N, errores, color='steelblue', s=10, zorder=3)
        ax_err.set_xlabel('Número de pasos (N)')
        ax_err.set_ylabel('|V(N) − V(500)|')
        ax_err.set_title(f'Error respecto al precio de referencia (N=500, V={p_ref:.6f})')
        ax_err.set_yscale('log')
        ax_err.grid(True, alpha=0.3)
        st.pyplot(fig_err)
        plt.close()
        st.caption("Escala logarítmica. El error disminuye al aumentar N.")
 
        st.divider()
        st.subheader("Frontera de ejercicio óptimo")
        N_frontera = 100
        _, S_arbol, _, E_arbol, _, _, _, dt_arbol = construir_arbol(S0, K, T, r, sigma, tipo, N=N_frontera)
        tiempos_frontera = []
        precios_frontera = []
        for i in range(N_frontera):
            precios_ejercicio = [S_arbol[j, i] for j in range(i + 1) if E_arbol[j, i]]
            if precios_ejercicio:
                precios_frontera.append(max(precios_ejercicio) if tipo == 'put' else min(precios_ejercicio))
                tiempos_frontera.append(i * dt_arbol)
        fig_front, ax_front = plt.subplots(figsize=(10, 4))
        if tiempos_frontera:
            ax_front.plot(tiempos_frontera, precios_frontera, color='steelblue', linewidth=2.0, label='Frontera')
            ax_front.fill_between(tiempos_frontera, precios_frontera,
                0 if tipo == 'put' else max(precios_frontera) * 1.5, alpha=0.1, color='steelblue', label='Zona de ejercicio')
        else:
            ax_front.text(0.5, 0.5, 'No se detecta ejercicio anticipado', ha='center', va='center',
                         transform=ax_front.transAxes, fontsize=12, color='gray')
        ax_front.axhline(K, color='goldenrod', linewidth=1.0, linestyle=':', label=f'K = {K}')
        ax_front.set_xlabel('Tiempo (años)')
        ax_front.set_ylabel('S')
        ax_front.set_title('Frontera de ejercicio óptimo')
        ax_front.legend()
        ax_front.grid(True, alpha=0.3)
        st.pyplot(fig_front)
        plt.close()
 
        st.divider()
        st.subheader("Árbol de valores (N=5)")
        _, S_arb5, V_arb5, E_arb5, u5, d5, p5, _ = construir_arbol(S0, K, T, r, sigma, tipo, N=5)
        fig_arb, ax_arb = plt.subplots(figsize=(14, 7))
        for i in range(6):
            for j in range(i + 1):
                x, y = i, i - 2 * j
                cs = 'darkorange' if E_arb5[j, i] else 'steelblue'
                cv = 'darkorange' if E_arb5[j, i] else 'firebrick'
                ax_arb.text(x, y + 0.18, f'S={S_arb5[j,i]:.2f}', ha='center', fontsize=7, color=cs, fontweight='bold')
                ax_arb.text(x, y - 0.18, f'V={V_arb5[j,i]:.2f}', ha='center', fontsize=7, color=cv)
                if i < 5:
                    ax_arb.plot([x, i+1], [y, (i+1)-2*j], color='green', linewidth=0.7, alpha=0.4)
                    ax_arb.plot([x, i+1], [y, (i+1)-2*(j+1)], color='red', linewidth=0.7, alpha=0.4)
        ax_arb.set_xlim(-0.5, 5.5)
        ax_arb.set_title(f'Árbol CRR — N=5 — {tipo.upper()}', fontsize=13)
        ax_arb.set_xlabel('Paso temporal')
        ax_arb.set_yticks([])
        ax_arb.set_facecolor('#fafafa')
        ax_arb.grid(False)
        st.pyplot(fig_arb)
        plt.close()
        st.caption(f"Azul: sin ejercicio. Naranja: ejercicio óptimo. u={u5:.4f}, d={d5:.4f}, p*={p5:.4f}")
 
    # --- Tab 3: Diferencias finitas ---
    with tab3:
        st.subheader("Perfil de valor (t = 0)")
        if tipo == 'call':
            intrinseco = np.maximum(S_grid - K, 0.0)
        else:
            intrinseco = np.maximum(K - S_grid, 0.0)
        mascara = (S_grid >= K * 0.3) & (S_grid <= K * 2.0)
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        ax4.plot(S_grid[mascara], V_grid[mascara], color='seagreen', linewidth=2.0, label=f'{tipo.upper()} americana')
        ax4.plot(S_grid[mascara], intrinseco[mascara], color='gray', linewidth=1.0, linestyle='--', label='Valor intrínseco')
        ax4.axvline(S0, color='goldenrod', linewidth=1.2, linestyle=':', label=f'S₀ = {S0}')
        ax4.axvline(K, color='silver', linewidth=0.8, linestyle=':', label=f'K = {K}')
        ax4.set_xlabel('S')
        ax4.set_ylabel('V(S)')
        ax4.set_title('Perfil de valor — Crank-Nicolson')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        st.pyplot(fig4)
        plt.close()
 
        st.divider()
        _, S_malla, tiempos_malla, V_malla = resolver_malla_completa(S0, K, T, r, sigma, tipo, N_S=150, N_T=600, n_fotos=80)
        mascara_m = (S_malla >= K * 0.3) & (S_malla <= K * 2.0)
 
        st.subheader("Evolución temporal del valor")
        indices_tiempo = np.linspace(0, len(tiempos_malla) - 1, 6, dtype=int)
        colores_evol = plt.cm.viridis(np.linspace(0.1, 0.9, len(indices_tiempo)))
        fig_evol, ax_evol = plt.subplots(figsize=(10, 5))
        for idx_t, color in zip(indices_tiempo, colores_evol):
            t_val = tiempos_malla[idx_t]
            V_t = V_malla[:, idx_t]
            label = f't = {t_val:.2f}'
            if t_val < 0.01: label = 't ≈ 0 (hoy)'
            elif abs(t_val - T) < 0.02: label = 't = T'
            ax_evol.plot(S_malla[mascara_m], V_t[mascara_m], color=color, linewidth=1.5, label=label)
        intr_m = np.maximum(S_malla - K, 0.0) if tipo == 'call' else np.maximum(K - S_malla, 0.0)
        ax_evol.plot(S_malla[mascara_m], intr_m[mascara_m], color='gray', linewidth=1.0, linestyle=':', label='Intrínseco')
        ax_evol.set_xlabel('S')
        ax_evol.set_ylabel('V(S,t)')
        ax_evol.set_title('Evolución temporal')
        ax_evol.legend(fontsize=8)
        ax_evol.grid(True, alpha=0.3)
        st.pyplot(fig_evol)
        plt.close()
        st.caption("Cada curva corresponde a un instante distinto. Al acercarse al vencimiento, converge al payoff.")
 
        st.divider()
        st.subheader("Frontera de ejercicio óptimo")
        tiempos_front_fd, precios_front_fd = [], []
        for idx_t in range(len(tiempos_malla)):
            V_t = V_malla[:, idx_t]
            intr_t = np.maximum(S_malla - K, 0.0) if tipo == 'call' else np.maximum(K - S_malla, 0.0)
            ejercicio = (np.abs(V_t - intr_t) < 1e-4) & (intr_t > 0.01)
            if np.any(ejercicio):
                precios_front_fd.append(np.max(S_malla[ejercicio]) if tipo == 'put' else np.min(S_malla[ejercicio]))
                tiempos_front_fd.append(tiempos_malla[idx_t])
        fig_ffd, ax_ffd = plt.subplots(figsize=(10, 4))
        if tiempos_front_fd:
            ax_ffd.plot(tiempos_front_fd, precios_front_fd, color='seagreen', linewidth=2.0, label='Frontera')
            ax_ffd.fill_between(tiempos_front_fd, precios_front_fd,
                0 if tipo == 'put' else max(precios_front_fd) * 1.5, alpha=0.1, color='seagreen')
        else:
            ax_ffd.text(0.5, 0.5, 'No se detecta ejercicio anticipado', ha='center', va='center',
                       transform=ax_ffd.transAxes, fontsize=12, color='gray')
        ax_ffd.axhline(K, color='goldenrod', linewidth=1.0, linestyle=':', label=f'K = {K}')
        ax_ffd.set_xlabel('Tiempo (años)')
        ax_ffd.set_ylabel('S')
        ax_ffd.set_title('Frontera de ejercicio — Dif. finitas')
        ax_ffd.legend()
        ax_ffd.grid(True, alpha=0.3)
        st.pyplot(fig_ffd)
        plt.close()
 
        st.divider()
        st.subheader("Mapa de calor V(S, t)")
        idx_s_min = np.searchsorted(S_malla, K * 0.3)
        idx_s_max = np.searchsorted(S_malla, K * 2.0)
        fig_heat, ax_heat = plt.subplots(figsize=(10, 5))
        im = ax_heat.pcolormesh(tiempos_malla, S_malla[idx_s_min:idx_s_max], V_malla[idx_s_min:idx_s_max, :], cmap='YlGnBu', shading='auto')
        fig_heat.colorbar(im, ax=ax_heat, label='V(S, t)')
        ax_heat.axhline(K, color='white', linewidth=1.0, linestyle='--', alpha=0.7, label=f'K = {K}')
        ax_heat.axhline(S0, color='goldenrod', linewidth=1.0, linestyle=':', alpha=0.7, label=f'S₀ = {S0}')
        ax_heat.set_xlabel('Tiempo (años)')
        ax_heat.set_ylabel('S')
        ax_heat.set_title('Mapa de calor — V(S, t)')
        ax_heat.legend(loc='upper right', fontsize=8)
        st.pyplot(fig_heat)
        plt.close()
 
    # --- Tab 4: Monte Carlo ---
    with tab4:
        st.subheader("Trayectorias simuladas")
        pasos_t = np.linspace(0, T, trayectorias.shape[1])
        np.random.seed(0)
        idx_muestra = np.random.choice(trayectorias.shape[0], size=50, replace=False)
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        for i in idx_muestra:
            ax5.plot(pasos_t, trayectorias[i, :], linewidth=0.5, alpha=0.5)
        ax5.axhline(K, color='firebrick', linewidth=1.2, linestyle='--', label=f'K = {K}')
        ax5.axhline(S0, color='goldenrod', linewidth=1.0, linestyle=':', label=f'S₀ = {S0}')
        ax5.set_xlabel('Tiempo (años)')
        ax5.set_ylabel('S')
        ax5.set_title('Trayectorias simuladas')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        st.pyplot(fig5)
        plt.close()
        st.caption(f"50 de {M_mc} trayectorias.")
 
        st.divider()
        st.subheader("Distribución del precio final S(T)")
        S_T = trayectorias[:, -1]
        fig_hs, ax_hs = plt.subplots(figsize=(10, 4))
        ax_hs.hist(S_T, bins=80, color='indianred', alpha=0.7, edgecolor='white', linewidth=0.3)
        ax_hs.axvline(K, color='goldenrod', linewidth=2.0, linestyle='--', label=f'K = {K}')
        ax_hs.axvline(np.mean(S_T), color='white', linewidth=1.2, label=f'Media = {np.mean(S_T):.2f}')
        ax_hs.set_xlabel('S(T)')
        ax_hs.set_ylabel('Frecuencia')
        ax_hs.set_title('Distribución del precio al vencimiento')
        ax_hs.legend()
        ax_hs.grid(True, alpha=0.3)
        st.pyplot(fig_hs)
        plt.close()
        pct_itm = np.mean(S_T < K) * 100 if tipo == 'put' else np.mean(S_T > K) * 100
        st.caption(f"Un {pct_itm:.1f}% de las trayectorias terminan in-the-money.")
 
        st.divider()
        st.subheader("Distribución del payoff descontado")
        payoff_pos = flujos_desc[flujos_desc > 0]
        payoff_cero = np.sum(flujos_desc == 0)
        fig_hp, ax_hp = plt.subplots(figsize=(10, 4))
        if len(payoff_pos) > 0:
            ax_hp.hist(payoff_pos, bins=60, color='indianred', alpha=0.7, edgecolor='white', linewidth=0.3)
        ax_hp.axvline(p_mc, color='goldenrod', linewidth=2.0, linestyle='--', label=f'Precio MC = {p_mc:.4f}')
        ax_hp.set_xlabel('Payoff descontado')
        ax_hp.set_ylabel('Frecuencia')
        ax_hp.set_title('Distribución del payoff (trayectorias con ejercicio)')
        ax_hp.legend()
        ax_hp.grid(True, alpha=0.3)
        st.pyplot(fig_hp)
        plt.close()
        st.caption(f"{payoff_cero} trayectorias ({payoff_cero/M_mc*100:.1f}%) expiran sin valor.")
 
        st.divider()
        st.subheader("Convergencia del estimador")
        media_acum = np.cumsum(flujos_desc) / np.arange(1, len(flujos_desc) + 1)
        n_tray = np.arange(1, len(flujos_desc) + 1)
        var_acum = np.cumsum((flujos_desc - media_acum)**2) / n_tray
        std_acum = np.sqrt(var_acum / n_tray)
        paso_plot = max(1, len(media_acum) // 500)
        idx_plot = np.arange(0, len(media_acum), paso_plot)
        fig_conv, ax_conv = plt.subplots(figsize=(10, 4))
        ax_conv.plot(n_tray[idx_plot], media_acum[idx_plot], color='indianred', linewidth=1.2, label='Estimación MC')
        ax_conv.fill_between(n_tray[idx_plot], (media_acum - 1.96*std_acum)[idx_plot],
                            (media_acum + 1.96*std_acum)[idx_plot], color='indianred', alpha=0.15, label='IC 95%')
        ax_conv.axhline(p_bin, color='steelblue', linewidth=1.0, linestyle='--', label=f'Binomial = {p_bin:.4f}')
        ax_conv.set_xlabel('Trayectorias')
        ax_conv.set_ylabel('Precio')
        ax_conv.set_title('Convergencia del estimador Monte Carlo')
        ax_conv.legend(fontsize=8)
        ax_conv.grid(True, alpha=0.3)
        st.pyplot(fig_conv)
        plt.close()
        st.caption("La banda sombreada es el intervalo de confianza al 95%.")
 
    # --- Tab 5: Griegas ---
    with tab5:
        st.subheader("Comparación de las griegas")
 
        st.markdown(f"""
        | Griega | Binomial | Dif. finitas | Monte Carlo |
        |--------|----------|-------------|-------------|
        | Delta (Δ) | {g_bin['Delta']:+.6f} | {g_fd['Delta']:+.6f} | {g_mc['Delta']:+.6f} |
        | Gamma (Γ) | {g_bin['Gamma']:+.6f} | {g_fd['Gamma']:+.6f} | {g_mc['Gamma']:+.6f} |
        | Theta (Θ) | {g_bin['Theta']:+.6f} | {g_fd['Theta']:+.6f} | {g_mc['Theta']:+.6f} |
        | Vega (ν) | {g_bin['Vega']:+.4f} | {g_fd['Vega']:+.4f} | {g_mc['Vega']:+.4f} |
        | Rho (ρ) | {g_bin['Rho']:+.4f} | {g_fd['Rho']:+.4f} | {g_mc['Rho']:+.4f} |
        """)
 
        griegas_peq = ['Delta', 'Gamma', 'Theta']
        griegas_gra = ['Vega', 'Rho']
        fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(13, 5))
        x = np.arange(len(griegas_peq))
        ancho = 0.25
        ax6a.bar(x - ancho, [g_bin[g] for g in griegas_peq], ancho, color='steelblue', alpha=0.8, label='Binomial')
        ax6a.bar(x, [g_fd[g] for g in griegas_peq], ancho, color='seagreen', alpha=0.8, label='Dif. finitas')
        ax6a.bar(x + ancho, [g_mc[g] for g in griegas_peq], ancho, color='indianred', alpha=0.8, label='Monte Carlo')
        ax6a.set_xticks(x)
        ax6a.set_xticklabels(griegas_peq)
        ax6a.set_title('Delta, Gamma y Theta')
        ax6a.legend(fontsize=9)
        ax6a.axhline(0, color='gray', linewidth=0.5)
        ax6a.grid(True, alpha=0.3)
        x2 = np.arange(len(griegas_gra))
        ax6b.bar(x2 - ancho, [g_bin[g] for g in griegas_gra], ancho, color='steelblue', alpha=0.8, label='Binomial')
        ax6b.bar(x2, [g_fd[g] for g in griegas_gra], ancho, color='seagreen', alpha=0.8, label='Dif. finitas')
        ax6b.bar(x2 + ancho, [g_mc[g] for g in griegas_gra], ancho, color='indianred', alpha=0.8, label='Monte Carlo')
        ax6b.set_xticks(x2)
        ax6b.set_xticklabels(griegas_gra)
        ax6b.set_title('Vega y Rho')
        ax6b.legend(fontsize=9)
        ax6b.axhline(0, color='gray', linewidth=0.5)
        ax6b.grid(True, alpha=0.3)
        plt.suptitle('Comparación de griegas entre los tres métodos', fontsize=13, y=1.02)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()
 
    # --- Tab 6: Conclusiones ---
    with tab6:
        st.subheader("Conclusiones del análisis")
 
        precios_dict = {'Binomial': p_bin, 'Dif. finitas': p_fd, 'Monte Carlo': p_mc}
        tiempos_dict = {'Binomial': t_bin, 'Dif. finitas': t_fd, 'Monte Carlo': t_mc}
 
        p_min = min(precios_dict.values())
        p_max = max(precios_dict.values())
        rango = p_max - p_min
 
        difs_vs_bin = {'Dif. finitas': abs(p_fd - p_bin), 'Monte Carlo': abs(p_mc - p_bin)}
        mas_alejado = max(difs_vs_bin, key=difs_vs_bin.get)
 
        mas_rapido = min(tiempos_dict, key=tiempos_dict.get)
        mas_lento = max(tiempos_dict, key=tiempos_dict.get)
        ratio_velocidad = tiempos_dict[mas_lento] / tiempos_dict[mas_rapido]
 
        prima_ea = p_bin - p_eu
        prima_pct = (prima_ea / p_eu * 100) if p_eu > 0 else 0
 
        # 1. Precios
        st.markdown("#### 1. Comparación de precios")
        st.markdown(
            f"Los tres métodos producen precios dentro de un rango estrecho: "
            f"**{p_min:.4f}** a **{p_max:.4f}** (diferencia máxima de {rango:.4f}). "
            f"El método que más se desvía del binomial es **{mas_alejado}**, "
            f"con una diferencia de {difs_vs_bin[mas_alejado]:.4f}."
        )
        if tipo == 'put':
            st.markdown(
                f"La prima de ejercicio anticipado es **{prima_ea:.4f}**, lo que representa "
                f"un **{prima_pct:.1f}%** sobre el precio europeo ({p_eu:.4f}). "
                f"Esto confirma que para una put americana el derecho a ejercer antes "
                f"del vencimiento tiene un valor apreciable."
            )
        else:
            st.markdown(
                f"La prima de ejercicio anticipado es **{prima_ea:.4f}**, prácticamente nula. "
                f"Esto es coherente con el resultado teórico: para una call americana "
                f"(en ausencia de reparto de beneficios al accionista) "
                f"nunca resulta óptimo ejercer antes del vencimiento. "
                f"El precio americano y el europeo coinciden."
            )
 
        st.divider()
 
        # 2. Velocidad
        st.markdown("#### 2. Comparación de velocidad")
        st.markdown(
            f"El método más rápido es **{mas_rapido}** ({tiempos_dict[mas_rapido]:.1f} ms) "
            f"y el más lento es **{mas_lento}** ({tiempos_dict[mas_lento]:.1f} ms). "
            f"La diferencia es de **{ratio_velocidad:.0f}x**."
        )
        if difs_vs_bin[mas_alejado] < 0.05 and tiempos_dict[mas_lento] > 500:
            st.markdown(
                f"Aunque {mas_lento} tarda considerablemente más, la mejora en precisión "
                f"respecto a los otros métodos no compensa el coste computacional adicional "
                f"para este escenario concreto."
            )
        elif difs_vs_bin[mas_alejado] < 0.01:
            st.markdown(
                f"Los tres métodos alcanzan una precisión similar, por lo que en este caso "
                f"el criterio de selección debería basarse en la velocidad de cálculo."
            )
 
        st.divider()
 
        # 3. Griegas
        st.markdown("#### 3. Comparación de las griegas")
        nombres_griegas = ['Delta', 'Gamma', 'Theta', 'Vega', 'Rho']
        dispersiones = {}
        for g in nombres_griegas:
            vals = [g_bin[g], g_fd[g], g_mc[g]]
            dispersiones[g] = max(vals) - min(vals)
 
        griega_estable = min(dispersiones, key=dispersiones.get)
        griega_inestable = max(dispersiones, key=dispersiones.get)
        desv_mc = {g: abs(g_mc[g] - g_bin[g]) for g in nombres_griegas}
        griega_mc_peor = max(desv_mc, key=desv_mc.get)
 
        st.markdown(
            f"La griega con mayor coincidencia entre los tres métodos es **{griega_estable}** "
            f"(dispersión de {dispersiones[griega_estable]:.6f}). "
            f"La de mayor dispersión es **{griega_inestable}** "
            f"(dispersión de {dispersiones[griega_inestable]:.4f})."
        )
        st.markdown(
            f"Monte Carlo presenta su mayor desviación en **{griega_mc_peor}** "
            f"(diferencia de {desv_mc[griega_mc_peor]:.4f} respecto al binomial). "
            f"Esto se debe al ruido inherente a la simulación aleatoria, que afecta "
            f"especialmente a las griegas calculadas como diferencias finitas sobre "
            f"un precio que ya es una estimación estadística."
        )
 
        st.divider()
 
        # 4. Recomendación
        st.markdown("#### 4. Recomendación para este escenario")
        if tipo == 'put':
            st.markdown(
                "Al tratarse de una **put americana**, el ejercicio anticipado es relevante "
                "y los tres métodos numéricos aportan información complementaria. "
                "El binomial resulta el más directo para observar la estructura de decisión "
                "nodo a nodo, las diferencias finitas ofrecen una solución continua sobre la malla, "
                "y Monte Carlo permite explorar la distribución de los resultados posibles."
            )
        else:
            st.markdown(
                "Al tratarse de una **call americana** (sin reparto de beneficios al accionista), "
                "el ejercicio anticipado no resulta óptimo en ningún punto. Esto implica que "
                "la fórmula cerrada de Black-Scholes para la opción europea es suficiente "
                "para obtener el precio. Los métodos numéricos confirman este resultado, "
                "pero no aportan información adicional relevante en este caso."
            )
        if sigma > 0.5:
            st.markdown(
                f"Con una volatilidad de {sigma:.0%}, que es alta, la estimación de Monte Carlo "
                f"puede presentar mayor variabilidad entre ejecuciones. "
                f"Los métodos de malla (binomial y diferencias finitas) tienden a ser más estables "
                f"en escenarios de alta volatilidad."
            )
        elif sigma < 0.10:
            st.markdown(
                f"Con una volatilidad de {sigma:.0%}, que es baja, todos los métodos convergen "
                f"rápidamente y las diferencias entre ellos son mínimas. "
                f"El valor temporal de la opción es reducido."
            )
 
        st.divider()
 
        # 5. Limitaciones
        st.markdown("#### 5. Limitaciones del análisis")
        st.markdown(
            """
            - Se asume volatilidad constante y tipo de interés fijo, condiciones que no se dan en mercados reales.
            - No se consideran costes de transacción ni impuestos.
            - El algoritmo LSM de Monte Carlo presenta un sesgo a la baja por la aproximación de la regresión en la decisión de ejercicio.
            - Las griegas se calculan mediante perturbaciones numéricas, lo que introduce un error adicional que depende del tamaño de la perturbación elegida.
            - Los resultados son sensibles a los parámetros numéricos de cada método (N, N_S, N_T, M). Valores demasiado bajos producen imprecisiones; valores altos incrementan el tiempo de cálculo.
            """
        )
 