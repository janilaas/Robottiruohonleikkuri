import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import timedelta

st.set_page_config(page_title="Robottiruohonleikkuri", layout="wide")
st.title("🌱 Robottiruohonleikkurin simulaatio")

st.sidebar.header("🔧 Parametrit")

pituus = st.sidebar.number_input("Alueen pituus (m)", min_value=1, value=10)
leveys = st.sidebar.number_input("Alueen leveys (m)", min_value=1, value=10)
leikkuusade = st.sidebar.number_input("Leikkuusäde (cm)", min_value=1, value=9)
nopeus_kmh = st.sidebar.number_input("Robottiruohonleikkurin nopeus (km/h)", min_value=0.1, value=1.0)
nopeutuskerroin = st.sidebar.slider("Simulaation nopeutuskerroin", 1, 100, 30)

if st.button("🚀 Käynnistä simulaatio"):
    st.subheader("Simulaatio käynnissä...")

    dx = 0.05  # ruudukon tarkkuus metreinä
    ny = int(pituus / dx)
    nx = int(leveys / dx)
    ruutu = np.zeros((ny, nx), dtype=bool)

    x = np.random.randint(0, nx)
    y = np.random.randint(0, ny)
    suunta = np.random.rand() * 2 * np.pi
    leikkuusade_m = leikkuusade / 100

    nopeus_mps = nopeus_kmh * 1000 / 3600
    dt = 1
    askel = int(nopeus_mps * dt / dx)
    t = 0
    max_iter = 1000000

    fig, ax = plt.subplots(figsize=(6, 6))
    plot = st.empty()
    status = st.empty()

    for i in range(max_iter):
        # Leikkaa ympyrä
        Y, X = np.ogrid[:ny, :nx]
        maski = (X * dx - x * dx)**2 + (Y * dx - y * dx)**2 <= leikkuusade_m**2
        ruutu[maski] = True

        # Laske uusi paikka
        uusi_x = x + int(np.cos(suunta) * askel)
        uusi_y = y + int(np.sin(suunta) * askel)

        # Jos uusi paikka ulkona rajojen, käänny takaisinpäin satunnaisesti
        if not (0 <= uusi_x < nx) or not (0 <= uusi_y < ny):
            suunta += np.pi + (np.random.rand() - 0.5) * np.pi / 2
            continue  # pysy paikoillaan tällä kierroksella
        else:
            x, y = uusi_x, uusi_y

        # Visualisointi
        if i % nopeutuskerroin == 0:
            ax.clear()
            ax.imshow(ruutu, cmap='Greens', origin='lower')
            ax.plot(x, y, 'ro')
            ax.set_title(f"Aika: {str(timedelta(seconds=t))} — Leikattu: {np.mean(ruutu) * 100:.1f}%")
            ax.axis('off')
            plot.pyplot(fig)

        if np.all(ruutu):
            break
        t += dt

    # Valmis!
    kesto = timedelta(seconds=t)
    st.success("✅ Alue on kokonaan leikattu!")
    st.markdown(f"""
    - ⏱️ **Aikaa kului:** {str(kesto)}
    - 🟩 **Leikattu alue:** {pituus * leveys:.1f} m²
    - 🚜 **Leikkuusäde:** {leikkuusade} cm (halkaisija {leikkuusade * 2} cm)
    - 💨 **Nopeus:** {nopeus_kmh} km/h
    """)

