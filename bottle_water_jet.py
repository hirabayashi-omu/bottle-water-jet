import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💧 ペットボトル噴流シミュレーター (並列表示・大きいラベル)")

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

# --- フレーム抽出 ---
n_frames = 6
indices = np.linspace(0, steps-1, n_frames, dtype=int)

# --- 1つのグラフに並べる ---
fig, axes = plt.subplots(1, n_frames, figsize=(18,6), sharey=True)

for ax, idx in zip(axes, indices):
    H = height[idx]
    width = d_nozzle / 1000
    x = np.array([-width/2, -width/2, width/2, width/2, -width/2])
    y = np.array([0, H, H, 0, 0])
    ax.fill(x, y, color="blue", alpha=0.6)
    
    ax.set_xlim(-0.01, 0.01)
    ax.set_ylim(0, 5)  # 縦軸5 m固定
    ax.set_xticks([])
    
    # 高さラベル大きく
    ax.set_ylabel("Height [m]", fontsize=14)
    ax.set_yticks(np.linspace(0, 5, 6))
    ax.set_yticklabels([f"{h:.1f}" for h in np.linspace(0, 5, 6)], fontsize=12)
    
    # 秒表示を大きく
    ax.set_title(f"{time[idx]:.1f} s", fontsize=16, color='red', fontweight='bold')

fig.tight_layout()
st.pyplot(fig)
st.caption("縦軸5 m固定で6フレームを並べ、時間ラベル・高さラベルを大きく表示しました。")
