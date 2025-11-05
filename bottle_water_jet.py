import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💧ペットボトル噴水シミュレーター（同軸噴流＋圧力減衰モデル）")

st.sidebar.header("入力パラメータ")

# --- 入力 ---
P0 = st.sidebar.slider("初期内圧 [気圧]", 1.0, 5.0, 2.0, 0.1)
r_ratio = st.sidebar.slider("外周流速度比 r（外流/中心流）", 0.0, 1.0, 0.2, 0.05)
Cd = st.sidebar.slider("流出係数 C_d", 0.3, 1.0, 0.7, 0.05)
eta_sys = st.sidebar.slider("システム効率 η", 0.1, 1.0, 0.6, 0.05)
d_nozzle = st.sidebar.slider("噴出孔直径 d [mm]", 1.0, 10.0, 3.0, 0.5)
fill_ratio = st.sidebar.slider("水の初期充填率", 0.3, 0.9, 0.5, 0.05)

# --- 定数 ---
rho = 1000.0  # 水 [kg/m³]
g = 9.81
Patm = 101325
P0_Pa = P0 * Patm

# --- 幾何と初期条件 ---
V_bottle = 1.5  # ← 固定：1.5 L
A_nozzle = np.pi * (d_nozzle / 1000 / 2) ** 2  # [m²]
V_bottle_m3 = V_bottle / 1000  # [m³]
V_water0 = V_bottle_m3 * fill_ratio
V_air0 = V_bottle_m3 - V_water0

# --- 時間発展設定 ---
dt = 0.001
t_max = 5.0
steps = int(t_max / dt)

# --- 配列初期化 ---
time = np.linspace(0, t_max, steps)
pressure = np.zeros(steps)
height = np.zeros(steps)
V_air = np.zeros(steps)
V_water = np.zeros(steps)

# 初期条件
P = P0_Pa
Vw = V_water0
Va = V_air0

# --- 時間ループ ---
for i in range(steps):
    if Vw <= 0:
        break  # 水が尽きたら終了

    # ボイルの法則 P*Va = P0*V0
    P = P0_Pa * V_air0 / Va

    # 流出速度（中心流＋外流平均）
    v_core = Cd * np.sqrt(2 * (P - Patm) / rho)
    v_outer = r_ratio * v_core
    v_eff = (v_core + v_outer) / 2

    # 噴出高さ
    H = eta_sys * v_eff**2 / (2 * g)

    # 流量 [m³/s]
    Q = A_nozzle * v_core

    # 体積更新
    Vw -= Q * dt
    Va = V_bottle_m3 - Vw

    # 記録
    pressure[i] = P / Patm  # atm表示
    height[i] = H
    V_water[i] = Vw
    V_air[i] = Va

# --- 結果表示 ---
st.subheader("🧮 計算結果")
st.write(f"**初期吹上げ高さ:** {height[0]:.2f} m")
st.write(f"**初期流量:** {A_nozzle * np.sqrt(2*(P0_Pa-Patm)/rho) * 1000:.2f} L/s")
st.write(f"**噴出時間:** {time[i]:.2f} 秒で水が尽きる")
st.write(f"(内圧 = {P0:.2f} 気圧, Cd = {Cd:.2f}, η = {eta_sys:.2f}, 外流比 r = {r_ratio:.2f}, ノズル径 = {d_nozzle:.1f} mm, ボトル容量 = 1.5 L)")

# --- プロット ---
fig, ax1 = plt.subplots()
ax1.plot(time[:i], height[:i], color="tab:blue", label="Jet height")
ax1.set_xlabel("time [s]", fontname="MS Gothic")
ax1.set_ylabel("Jet height [m]", color="tab:blue", fontname="MS Gothic")
ax1.tick_params(axis='y', labelcolor="tab:blue")

ax2 = ax1.twinx()
ax2.plot(time[:i], pressure[:i], color="tab:red", linestyle="--", label="inner pressure")
ax2.set_ylabel("inner pressure [atm]", color="tab:red", fontname="MS Gothic")
ax2.tick_params(axis='y', labelcolor="tab:red")

fig.tight_layout()
st.pyplot(fig)

st.caption("※ボイルの法則による内圧減衰を考慮。内圧の低下に伴い噴出高さが時間とともに減少します。")
