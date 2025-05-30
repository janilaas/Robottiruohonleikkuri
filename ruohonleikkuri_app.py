import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import pandas as pd
import io

st.set_page_config(page_title="Robottiruohonleikkuri", layout="wide")
st.title("🌿 Robottiruohonleikkurin simulaattori")

# Alkuvalikko
valinta = st.radio("Valitse toiminto:", ["Luo kerta-analyysi", "Luo data-aineisto analyysia varten"])

# Yleiset parametrit
pituus = st.sidebar.number_input("Alueen pituus (m)", min_value=1, value=10)
leveys = st.sidebar.number_input("Alueen leveys (m)", min_value=1, value=10)
leikkuusade = st.sidebar.number_input("Leikkuusäde (cm)", min_value=1, value=9)
nopeus_kmh = st.sidebar.number_input("Nopeus (km/h)", min_value=0.1, value=1.0)
leikkuuhalkaisija = 2 * leikkuusade / 100  # metreinä

# Simulaation ytimenä toimiva funktio
def suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh, visualisoi=False, nopeutuskerroin=30):
    dx = 0.05
    ny = int(pituus / dx)
    nx = int(leveys / dx)
    grid = np.zeros((ny, nx))

    x = np.random.uniform(0, leveys)
    y = np.random.uniform(0, pituus)
    suunta = np.random.rand() * 2 * np.pi
    nopeus_mps = nopeus_kmh * 1000 / 3600
    dt = 1
    askel_x = np.cos(suunta) * nopeus_mps * dt
    askel_y = np.sin(suunta) * nopeus_mps * dt
    t = 0
    kaannokset = 0

    x1, y1 = x, y
    if visualisoi:
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

        px, py = x1, y1
        steps = int(np.hypot(x2 - x1, y2 - y1) / dx)
        for s in range(steps):
            px += (x2 - x1) / steps
            py += (y2 - y1) / steps
            merkitse_leikattu(px, py)

        x1, y1 = x2, y2
        t += dt

        leikattu_ala = np.sum(grid) * (dx ** 2)
        koko_ala = pituus * leveys
        leikattu_prosentti = (leikattu_ala / koko_ala) * 100

        if visualisoi and len(np.where(grid == 1)[0]) % nopeutuskerroin == 0:
            ax.clear()
            ax.imshow(grid, extent=[0, leveys, 0, pituus], origin='lower', cmap='Greens', alpha=0.8)
            ax.set_xlim(0, leveys)
            ax.set_ylim(0, pituus)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f"Aika: {str(timedelta(seconds=t))} | Leikattu osuus: {leikattu_prosentti:.1f}%")
            plot.pyplot(fig)

        if np.all(grid == 1):
            break

    return t, leikattu_ala, kaannokset

# ---------------------
# KERTA-ANALYYSI
# ---------------------
if valinta == "Luo kerta-analyysi":
    nopeutuskerroin = st.sidebar.slider("Simulaation nopeutuskerroin", 1, 100, 30)
    if st.button("🚀 Käynnistä simulaatio"):
        st.subheader("Simulaatio käynnissä...")
        t, leikattu_ala, kaannokset = suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh, True, nopeutuskerroin)

        st.success("✅ Simulaatio valmis!")
        st.markdown(f"""
        - ⏱️ **Aikaa kului:** {str(timedelta(seconds=t))}
        - 🔁 **Käännöksiä:** {kaannokset}
        - 🟩 **Leikattua pinta-alaa:** {leikattu_ala:.2f} m²
        - ✂️ **Leikkuuhalkaisija:** {leikkuuhalkaisija:.2f} m
        """)

# ---------------------
# DATA-AINEISTON LUONTI
# ---------------------
else:
    maara = st.number_input("Montako simulaatiota suoritetaan?", min_value=1, value=10)
    if st.button("📊 Suorita simulaatiot ja luo data"):
        tulokset = []
        for i in range(maara):
            t, leikattu_ala, kaannokset = suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh, visualisoi=False)
            tulokset.append({
                "Simulaatio": i + 1,
                "Aika (s)": t,
                "Aika (hh:mm:ss)": str(timedelta(seconds=t)),
                "Leikattu ala (m²)": round(leikattu_ala, 2),
                "Käännöksiä": kaannokset,
                "Leikkuuhalkaisija (m)": leikkuuhalkaisija,
                "Nopeus (km/h)": nopeus_kmh,
                "Alue (m²)": pituus * leveys
            })

        df = pd.DataFrame(tulokset)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Lataa CSV",
            data=csv,
            file_name='robottiruohonleikkuri_data.csv',
            mime='text/csv'
        )
