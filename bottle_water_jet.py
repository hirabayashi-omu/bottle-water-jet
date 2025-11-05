import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

st.title("💧 ペットボトル噴流アニメーション")

# --- サイドバー入力パラメータ ---
P0 = st.sidebar.slider("初期圧力 [atm]", 1.0, 6.0, 2.0, 0.1)
eta_sys = st.sidebar.slider("系のエネルギー効率 η", 0.01, 1.0, 0.6, 0.05)
d_nozzle = st.sidebar.slider("ノズル径 d [mm]", 1.0, 10.0, 3.0, 0.5)
fill_ratio = st.sidebar.slider("初期液充てん率", 0.01, 0.99, 0.5, 0.05)

# --- 定数 ---
rho = 1000.0
g = 9.81
Patm = 101325
P0_Pa = P0 * Patm
V_bottle = 1.5        # L
A_nozzle = np.pi * (d_nozzle / 1000 / 2) ** 2  # m²
V_bottle_m3 = V_bottle / 1000
V_water0 = V_bottle_m3 * fill_ratio
V_air0 = V_bottle_m3 - V_water0

# --- 時間設定 ---
dt = 0.01
t_max = 5.0
steps = int(t_max / dt)
time = np.linspace(0, t_max, steps)

# --- 高さ計算 ---
height = np.zeros(steps)
Vw = V_water0
Va = V_air0
gamma = 1.4

for i in range(steps):
    if Vw <= 0:
        height[i:] = 0
        break
    P = P0_Pa * (V_air0 / Va) ** gamma
    v_eff = np.sqrt(2 * (P - Patm) / rho)
    H = eta_sys * v_eff**2 / (2 * g)
    height[i] = H
    # outflow
    Q = A_nozzle * v_eff
    dV = Q * dt
    Vw -= dV
    Va = V_bottle_m3 - Vw

# --- アニメーション作成 ---
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

ani = FuncAnimation(fig, update, frames=steps, interval=20, blit=True)

# --- 動画保存 ---
video_path = "/tmp/bottle_jet.mp4"
ani.save(video_path, writer='ffmpeg', fps=30)

# --- Streamlit で動画表示 ---
st.video(video_path)

st.caption("サイドバーでパラメータを調整して、噴流高さと水流の広がりを可視化できます。")
