import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💧 ペットボトル噴流シミュレーター (静止フレーム版)")

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
V_bottle = 1.5  # L
A_nozzle = np.pi * (d_nozzle / 1000 / 2) ** 2
V_bottle_m3 = V_bottle / 1000
V_water0 = V_bottle_m3 * fill_ratio
V_air0 = V_bottle_m3 - V_water0

# --- Time evolution ---
dt = 0.01
t_max = 5.0
steps = int(t_max / dt)
time = np.linspace(0, t_max, steps)
height = np.zeros(steps)
Vw = V_water0
Va = V_air0
gamma = 1.4

for i in range(steps):
    if Vw <= 0:
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
    height[i] = H

# --- 複数時刻の水柱を並べて表示 ---
n_frames = 6  # 表示するフレーム数
indices = np.linspace(0, steps-1, n_frames, dtype=int)

fig, axes = plt.subplots(1, n_frames, figsize=(n_frames*2,6), sharey=True)

for ax, idx in zip(axes, indices):
    H = height[idx]
    x = np.linspace(-0.005, 0.005, 5)
    y = H * (1 - (x/0.005)**2)
    ax.plot(x, y, color="blue", linewidth=4, alpha=0.6)
    ax.set_title(f"t={time[idx]:.2f}s")
    ax.set_xlim(-0.01,0.01)
    ax.set_ylim(0, max(height)*1.2)
    ax.set_xticks([])
    ax.set_xlabel("X")
axes[0].set_ylabel("Height [m]")

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)  # ← ここを追加してDOMノードの競合を防ぐ

# --- 計算結果 ---
st.subheader("🧮 計算結果")
st.write(f"**初期噴出高さ:** {height[0]:.2f} m")
st.write(f"**初期噴出速度:** {A_nozzle * np.sqrt(2*(P0_Pa-Patm)/rho) * 1000:.2f} L/s")
st.write(f"**液が空になるまでの時間:** {time[i]:.2f} s")
st.write(f"(P₀ = {P0:.2f} atm, η = {eta_sys:.2f}, r = {r_ratio:.2f}, d = {d_nozzle:.1f} mm, L = {L_nozzle:.1f} mm, Cd = {Cd:.3f})")

st.caption("複数の時間での水柱を並べて表示しています。動画化せずに時間変化を視覚化可能です。")
