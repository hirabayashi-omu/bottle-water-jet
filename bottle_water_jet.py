import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💧ペットボトル噴水シミュレーター（同軸噴流モデル）")

st.sidebar.header("入力パラメータ")

# --- 入力 ---
P0 = st.sidebar.slider("初期内圧 [気圧]", 1.0, 5.0, 2.0, 0.1)
r_ratio = st.sidebar.slider("外周流速度比 r（外流/中心流）", 0.0, 1.0, 0.2, 0.05)
Cd = st.sidebar.slider("流出係数 C_d（縮流・摩擦損失）", 0.3, 1.0, 0.7, 0.05)
eta_sys = st.sidebar.slider("システム効率 η（噴流損失）", 0.1, 1.0, 0.6, 0.05)

# --- 定数 ---
rho = 1000.0  # 水 [kg/m3]
g = 9.81
Patm = 1.0 * 101325
P0_Pa = P0 * 101325

# --- 吹上げ高さ計算 ---
deltaP = P0_Pa - Patm
v_core = Cd * np.sqrt(2 * deltaP / rho)
v_outer = r_ratio * v_core
v_eff = (v_core + v_outer) / 2

H = eta_sys * (v_eff**2) / (2 * g)

# --- 結果表示 ---
st.subheader("🧮 計算結果")
st.write(f"**吹上げ高さの推定値:** {H:.2f} m")
st.write(f"(内圧 = {P0:.2f} 気圧, Cd = {Cd:.2f}, η = {eta_sys:.2f}, 外周流速度比 r = {r_ratio:.2f})")

# --- 時間発展プロット ---
t_max = 2 * v_eff / g
time = np.linspace(0, t_max, 200)
height = v_eff * time - 0.5 * g * time**2
height[height < 0] = 0

# 圧力変化（簡易的に線形減少と仮定）
pressure = P0 - (P0 - 1.0) * (time / max(time))

fig, ax1 = plt.subplots()
ax1.plot(time, height, color="tab:blue", label="Jet Ejection Simulation from a Bottle")
ax1.set_xlabel("time [sec]", fontname="MS Gothic")
ax1.set_ylabel("jet hight [m]", color="tab:blue", fontname="MS Gothic")
ax1.tick_params(axis='y', labelcolor="tab:blue")

ax2 = ax1.twinx()
ax2.plot(time, pressure, color="tab:red", linestyle="--", label="gauge pressure")
ax2.set_ylabel("inner pressure [atm(G)]", color="tab:red", fontname="MS Gothic")
ax2.tick_params(axis='y', labelcolor="tab:red")

fig.tight_layout()
st.pyplot(fig)

st.caption("※縮流・摩擦・外流によるエネルギー損失を考慮しています。実際の吹上げ高さは実験条件でさらに低下します。")
