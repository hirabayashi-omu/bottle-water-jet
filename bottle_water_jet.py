import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

st.title("💧 ペットボトル噴流シミュレーター (動画版)")

# --- サイドバーパラメータ ---
P0 = st.sidebar.slider("初期圧力 [atm]", 1.0, 6.0, 2.0, 0.1)
r_ratio = st.sidebar.slider("外周流速度比 r（外流/中心流)", 0.0, 1.0, 0.2, 0.05)
eta_sys = st.sidebar.slider("系のエネルギー効率 η", 0.01, 1.0, 0.6, 0.05)
d_nozzle = st.sidebar.slider("ノズル径 d [mm]", 1.0, 10.0, 3.0, 0.5)
L_nozzle = st.sidebar.slider("ノズル長 L [mm]", 0.5, 10.0, 3.0, 0.5)
fill_ratio = st.sidebar.slider("初期液充てん率", 0.01, 0.99, 0.5, 0.05)

# --- Derived flow coefficient ---
L_over_d = L_nozzle / d_nozzle
Cd = 0.611 + 0.08 * np.exp(-3 * L_over_d)
Cd = np.clip(Cd, 0.3, 1.0)
st.sidebar.write(f"**流出係数 Cd:** {Cd:.3f}")

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
gamma = 1.4

# --- Time loop (噴出高さ計算) ---
for i in range(steps):
    if Vw <= 0:
        height[i:] = 0
        pressure[i:] = Patm
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

# --- Animation (簡易2D水柱) ---
fig, ax = plt.subplots(figsize=(5,6))
ax.set_xlim(-0.05, 0.05)
ax.set_ylim(0, max(height)*1.2)
ax.set_xlabel("X [m]")
ax.set_ylabel("Height [m]")
ax.set_title("ペットボトル噴流の可視化")
line, = ax.plot([], [], color="blue", linewidth=4, alpha=0.6)

def update(frame):
    H = height[frame]
    x = np.linspace(-0.005, 0.005, 5)
    y = H * (1 - (x/0.005)**2)
    line.set_data(x, y)
    return line,

ani = FuncAnimation(fig, update, frames=steps, interval=10, blit=True)

# --- 動画保存 & Streamlit 表示 ---
video_path = "/tmp/bottle_jet.mp4"
ani.save(video_path, writer='ffmpeg', fps=60)
st.video(video_path)

# --- 結果表示 ---
st.subheader("🧮 計算結果")
st.write(f"**初期噴出高さ:** {height[0]:.2f} m")
st.write(f"**初期噴出速度:** {A_nozzle * np.sqrt(2*(P0_Pa-Patm)/rho) * 1000:.2f} L/s")
st.write(f"**液が空になるまでの時間:** {time[i]:.2f} s")
st.write(f"(P₀ = {P0:.2f} atm, η = {eta_sys:.2f}, r = {r_ratio:.2f}, d = {d_nozzle:.1f} mm, L = {L_nozzle:.1f} mm, Cd = {Cd:.3f})")

st.caption("水柱の幅はノズル径に応じ、噴出高さは内部圧力・系効率に応じて変化します。")
