import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💧 ペットボトル噴流シミュレーター (噴流 + 圧力減衰モデル)")

st.sidebar.header("入力パラメータ")

# --- Inputs ---
P0 = st.sidebar.slider("初期圧力 [atm]", 1.0, 5.0, 2.0, 0.1)
r_ratio = st.sidebar.slider("外周流速度比 r（外流/中心流)", 0.0, 1.0, 0.2, 0.05)
eta_sys = st.sidebar.slider("系のエネルギー効率 η", 0.1, 1.0, 0.6, 0.05)
d_nozzle = st.sidebar.slider("ノズル径 d [mm]", 1.0, 10.0, 3.0, 0.5)
L_nozzle = st.sidebar.slider("ノズル長 L [mm]", 0.5, 10.0, 3.0, 0.5)
fill_ratio = st.sidebar.slider("初期液充てん率", 0.3, 0.9, 0.5, 0.05)

# --- Derived flow coefficient ---
L_over_d = L_nozzle / d_nozzle
Cd = 0.611 + 0.08 * np.exp(-3 * L_over_d)
Cd = np.clip(Cd, 0.3, 1.0)  # physical bound

st.sidebar.write(f"**流出係数の推算値 Cd:** {Cd:.3f}")

# --- Constants ---
rho = 1000.0
g = 9.81
Patm = 101325
P0_Pa = P0 * Patm

# --- Geometry and initial conditions ---
V_bottle = 1.5  # L
A_nozzle = np.pi * (d_nozzle / 1000 / 2) ** 2  # m²
V_bottle_m3 = V_bottle / 1000  # m³
V_water0 = V_bottle_m3 * fill_ratio
V_air0 = V_bottle_m3 - V_water0

# --- Time evolution ---
dt = 0.001
t_max = 5.0
steps = int(t_max / dt)

time = np.linspace(0, t_max, steps)
pressure = np.zeros(steps)
height = np.zeros(steps)

# --- Initial values ---
P = P0_Pa
Vw = V_water0
Va = V_air0

# --- Time loop ---
for i in range(steps):
    if Vw <= 0:
        break

    # Adiabatic expansion (γ = 1.4)
    gamma = 1.4
    P = P0_Pa * (V_air0 / Va) ** gamma

    # Flow velocity
    v_core = Cd * np.sqrt(2 * (P - Patm) / rho)
    v_outer = r_ratio * v_core
    v_eff = (v_core + v_outer) / 2

    # Jet height
    H = eta_sys * v_eff**2 / (2 * g)

    # Outflow and volume update
    Q = A_nozzle * v_core
    dV = Q * dt
    Vw -= dV
    Va = V_bottle_m3 - Vw

    # Record
    pressure[i] = P / Patm
    height[i] = H

# --- Results ---
st.subheader("🧮 結果")
st.write(f"**初期噴出高さ:** {height[0]:.2f} m")
st.write(f"**初期噴出速度:** {A_nozzle * np.sqrt(2*(P0_Pa-Patm)/rho) * 1000:.2f} L/s")
st.write(f"**液が空になるまでの時間（固定）:** {time[i]:.2f} s")
st.write(f"(P₀ = {P0:.2f} atm, η = {eta_sys:.2f}, r = {r_ratio:.2f}, d = {d_nozzle:.1f} mm, L = {L_nozzle:.1f} mm, Cd = {Cd:.3f})")

# --- Plot ---
fig, ax1 = plt.subplots()
ax1.plot(time[:i], height[:i], color="tab:blue", label="Jet height")
ax1.set_xlabel("Time [s]", fontname="Arial")
ax1.set_ylabel("Jet height [m]", color="tab:blue", fontname="Arial")
ax1.tick_params(axis='y', labelcolor="tab:blue")

ax2 = ax1.twinx()
ax2.plot(time[:i], pressure[:i], color="tab:red", linestyle="--", label="Inner pressure")
ax2.set_ylabel("Inner pressure [atm]", color="tab:red", fontname="Arial")
ax2.tick_params(axis='y', labelcolor="tab:red")

fig.tight_layout()
st.pyplot(fig)

st.caption("The discharge coefficient C_d is automatically estimated from the nozzle geometry (L/d ratio). "
           "A smaller nozzle diameter or longer nozzle reduces outflow rate, delaying pressure decay and maintaining higher jet height.")
