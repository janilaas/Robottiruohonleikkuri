import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Robottiruohonleikkuri", layout="wide")
st.title("🌱 Robottiruohonleikkurin simulaatio")

st.sidebar.header("🔧 Parametrit")

pituus = st.sidebar.number_input("Alueen pituus (m)", min_value=1, value=10)
leveys = st.sidebar.number_input("Alueen leveys (m)", min_value=1, value=10)
leikkuusade = st.sidebar.number_input("Leikkuusäde (cm)", min_value=1, value=18)
nopeus_kmh = st.sidebar.number_input("Robottiruohonleikkurin nopeus (km/h)", min_value=1.0, value=1.0)
nopeutuskerroin = st.sidebar.slider("Simulaation nopeutuskerroin", 1, 100, 30)

if st.button("🚀 Käynnistä simulaatio"):
    st.subheader("Simulaatio käynnissä...")

    # Yksiköt
    dx = 0.05  # resoluutio (metreinä)
    ny = int(pituus / dx)
    nx = int(leveys / dx)
    ruutu = np.zeros((ny, nx), dtype=bool)

    # Alkuarvot
    x = np.random.randint(0, nx)
    y = np.random.randint(0, ny)
    suunta = np.random.rand() * 2 * np.pi
    leikkuusade_m = leikkuusade / 100

    # Ajan ja nopeuden asetukset
    nopeus_mps = nopeus_kmh * 1000 / 3600
    dt = 1
    askel = int(nopeus_mps * dt / dx)
    t = 0
    max_iter = 1000000

    fig, ax = plt.subplots(figsize=(6, 6))
    plot = st.empty()
    status = st.empty()

    for i in range(max_iter):
        # Leikataan ympyrä ruudulta
        Y, X = np.ogrid[:ny, :nx]
        maski = (X * dx - x * dx)**2 + (Y * dx - y * dx)**2 <= leikkuusade_m**2
        ruutu[maski] = True

        # Liikuta robottia satunnaisesti
        suunta += np.random.randn() * 0.5
        x += int(np.cos(suunta) * askel)
        y += int(np.sin(suunta) * askel)

        # Tarkista rajat
        x = max(0, min(nx - 1, x))
        y = max(0, min(ny - 1, y))

        # Visualisointi
        if i % nopeutuskerroin == 0:
            ax.clear()
            ax.imshow(ruutu, cmap='Greens', origin='lower')
            ax.plot(x, y, 'ro')
            ax.set_title(f"Aika: {int(t)} s — Leikattu: {np.mean(ruutu) * 100:.1f}%")
            ax.axis('off')
            plot.pyplot(fig)

        if np.all(ruutu):
            break
        t += dt

    # Yhteenveto
    st.success("✅ Alue on kokonaan leikattu!")
    st.markdown(f"""
    - ⏱️ **Aikaa kului:** {t} sekuntia ({t/60:.1f} min)
    - 🟩 **Leikattu alue:** {pituus * leveys} m²
    - 🚜 **Leikkuusäde:** {leikkuusade} cm
    - 💨 **Nopeus:** {nopeus_kmh} km/h
    """)

