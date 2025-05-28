import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

st.set_page_config(page_title="Robottiruohonleikkuri", layout="wide")
st.title("🌿 Robottiruohonleikkurin simulaatio – Leikkuuraidat näkyvissä")

st.sidebar.header("🔧 Parametrit")

# Käyttäjän syötteet
pituus = st.sidebar.number_input("Alueen pituus (m)", min_value=1, value=10)
leveys = st.sidebar.number_input("Alueen leveys (m)", min_value=1, value=10)
leikkuusade = st.sidebar.number_input("Leikkuusäde (cm)", min_value=1, value=9)
nopeus_kmh = st.sidebar.number_input("Nopeus (km/h)", min_value=0.1, value=1.0)
nopeutuskerroin = st.sidebar.slider("Simulaation nopeutuskerroin", 1, 100, 30)

if st.button("🚀 Käynnistä simulaatio"):
    st.subheader("Simulaatio käynnissä...")

    leikkuuhalkaisija = 2 * leikkuusade / 100  # m
    dx = 0.05
    ny = int(pituus / dx)
    nx = int(leveys / dx)
    grid = np.zeros((ny, nx))  # Alueen peitto, 0=leikkaamaton, 1=leikattu

    x = np.random.uniform(0, leveys)
    y = np.random.uniform(0, pituus)
    suunta = np.random.rand() * 2 * np.pi
    nopeus_mps = nopeus_kmh * 1000 / 3600
    dt = 1
    askel_x = np.cos(suunta) * nopeus_mps * dt
    askel_y = np.sin(suunta) * nopeus_mps * dt
    t = 0
    kaannokset = 0

    viivat = []
    x1, y1 = x, y

    fig, ax = plt.subplots(figsize=(6, 6))
    plot = st.empty()

    def merkitse_leikattu(x, y):
        cx = int(x / dx)
        cy = int(y / dx)
        r = int(leikkuuhalkaisija / (2 * dx))
        for i in range(max(0, cy - r), min(ny, cy + r)):
            for j in range(max(0, cx - r), min(nx, cx + r)):
                if np.hypot((j - cx), (i - cy)) * dx <= leikkuuhalkaisija / 2:
                    grid[i, j] = 1

    while True:
        x2 = x1 + askel_x
        y2 = y1 + askel_y

        if not (0 <= x2 <= leveys) or not (0 <= y2 <= pituus):
            kaannokset += 1
            suunta = np.random.rand() * 2 * np.pi
            askel_x = np.cos(suunta) * nopeus_mps * dt
            askel_y = np.sin(suunta) * nopeus_mps * dt
            x1 = np.clip(x2, 0, leveys)
            y1 = np.clip(y2, 0, pituus)
            continue

        viivat.append(((x1, y1), (x2, y2)))

        # Merkitään leikkuualuetta täksi viivan matkaksi
        px, py = x1, y1
        steps = int(np.hypot(x2 - x1, y2 - y1) / dx)
        for s in range(steps):
            px += (x2 - x1) / steps
            py += (y2 - y1) / steps
            merkitse_leikattu(px, py)

        x1, y1 = x2, y2
        t += dt

        if len(viivat) % nopeutuskerroin == 0:
            ax.clear()
            for (xa, ya), (xb, yb) in viivat:
                ax.plot([xa, xb], [ya, yb], color='green', linewidth=leikkuuhalkaisija/dx, alpha=0.7)

            ax.set_xlim(0, leveys)
            ax.set_ylim(0, pituus)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f"Aika: {str(timedelta(seconds=t))}, Käännöksiä: {kaannokset}")
            plot.pyplot(fig)

        # Lopetetaan kun kaikki ruudut on leikattu
        if np.all(grid == 1):
            break

    st.success("✅ Simulaatio valmis!")
    st.markdown(f"""
    - ⏱️ **Aikaa kului:** {str(timedelta(seconds=t))}
    - 🔁 **Käännöksiä tehtiin:** {kaannokset}
    - 🟩 **Leikattu alue:** {pituus * leveys:.1f} m²
    - ✂️ **Leikkuuhalkaisija:** {leikkuuhalkaisija:.2f} m
    """)
