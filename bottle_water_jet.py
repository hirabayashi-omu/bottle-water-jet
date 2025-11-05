import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# --- 日本語フォント設定（明示的指定）---
# Windows の MS Gothic のパスを直接登録
font_path = "C:/Windows/Fonts/msgothic.ttc"
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

st.set_page_config(page_title="水の吹上げ高さシミュレータ", layout="wide")

st.title("💧 ペットボトル噴流の吹上げ高さシミュレーション")

# --- 入力パラメータ ---
st.sidebar.header("入力パラメータ設定")
P0 = st.sidebar.slider("初期内圧 [気圧]", 0.1, 5.0, 2.0, 0.1)
r = st.sidebar.slider("外周流速度比 r", 0.0, 1.0, 0.2, 0.05)
eta = st.sidebar.slider("エネルギー変換効率 η", 0.01, 0.5, 0.05, 0.01)

# --- 物理パラメータ ---
rho = 1000  # 水の密度 [kg/m3]
P0_Pa = P0 * 101325  # [Pa]
Cd = 0.62  # 縮流係数
g = 9.81

# --- 噴流中心速度と吹上高さ ---
v_core = Cd * np.sqrt(2 * P0_Pa / rho) * (1 - r)
h = eta * (v_core ** 2) / (2 * g)

# --- 結果表示 ---
st.write(f"### 吹上げ高さの推定値: **{h:.2f} m**")
st.write(f"(効率 η={eta:.2f}, 外周流速度比 r={r:.2f}, 初期内圧 {P0:.2f} 気圧)")

# --- グラフ ---
fig, ax = plt.subplots(figsize=(7, 4))
P_list = np.linspace(0.1, 5, 50)
h_list = eta * (Cd * np.sqrt(2 * P_list * 101325 / rho) * (1 - r)) ** 2 / (2 * g)

ax.plot(P_list, h_list, color='royalblue', linewidth=2)
ax.set_xlabel("初期内圧 [気圧]", fontsize=12, fontproperties=font_prop)
ax.set_ylabel("吹上げ高さ [m]", fontsize=12, fontproperties=font_prop)
ax.set_title("内圧と吹上げ高さの関係", fontsize=14, fontproperties=font_prop)
ax.grid(True)

st.pyplot(fig)
