import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

st.title("💧 ペットボトル噴流アニメーション (噴流 + 圧力減衰)")

# --- パラメータ（省略、元コードと同じ） ---
P0 = st.sidebar.slider("初期圧力 [atm]", 1.0, 6.0, 2.0, 0.1)
r_ratio = st.sidebar.slider("外周流速度比 r（外流/中心流)", 0.0, 1.0, 0.2, 0.05)
eta_sys = st.sidebar.slider("系のエネルギー効率 η", 0.01, 1.0, 0.6, 0.05)
d_nozzle = st.sidebar.slider("ノズル径 d [mm]", 1.0, 10.0, 3.0, 0.5)
L_nozzle = st.sidebar.slider("ノズル長 L [mm]", 0.5, 10.0, 3.0, 0.5)
fill_ratio = st.sidebar.slider("初期液充てん率", 0.01, 0.99, 0.5, 0.05)

# 流出係数
L_over_d = L_nozzle / d_nozzle
Cd = 0.611 + 0.08 * np.exp(-3 * L_over_d)
Cd = np.clip(Cd, 0.3, 1.0)

# 定数
rho = 1000.0
g = 9.81
Patm = 101325
P0_Pa = P0 * Patm
V_bottle = 1.5
A_nozzle = np.pi * (d_nozzle / 1000 / 2) ** 2
V_bottle_m3 = V_bottle / 1000
V_water0 = V_bottle_m3 * fill_ratio
V_air0 = V_bottle_m3 - V_water0

# 時間設定
dt = 0.01
t_max = 5.0
steps = int(t_max / dt)
time = np.linspace(0, t_max, steps)
pressure = np.zeros(steps)
height = np.zeros(steps)

# 初期値
P = P0_Pa
Vw = V_water0
Va = V_air0
gamma = 1.4

# --- 計算 ---
for i in range(steps):
    if Vw <= 0:
        pressure[i:] = Patm
        height[i:] = 0
        break

    P = P0_Pa * (V_air0 / Va) ** gamma
    v_core = Cd * np.sqrt(2 * (P - Patm) / rho)
    v_outer = r_ratio * v_core
    v_eff = (v_core + v_outer) / 2
    H = eta_sys * v_eff**2 / (2 * g)
    
    Q = A_nozzle * v_core
    dV = Q * dt
    Vw -= dV
    Va = V_bottle_m3 - Vw

    pressure[i] = P / Patm
    height[i] = H

# --- アニメーション ---
fig, ax1 = plt.subplots(figsize=(6,4))
ax2 = ax1.twinx()
line1, = ax1.plot([], [], color="tab:blue")
line2, = ax2.plot([], [], color="tab:red", linestyle="--")
ax1.set_xlim(0, t_max)
ax1.set_ylim(0, max(height)*1.2)
ax2.set_ylim(0, max(pressure)*1.2)
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Jet height [m]", color="tab:blue")
ax2.set_ylabel("Pressure [atm]", color="tab:red")

def update(frame):
    line1.set_data(time[:frame], height[:frame])
    line2.set_data(time[:frame], pressure[:frame])
    return line1, line2

ani = FuncAnimation(fig, update, frames=steps, interval=20, blit=True)

st.pyplot(fig)
st.caption("アニメーション化により噴流高さと内部圧力の時間変化を可視化できます。")
