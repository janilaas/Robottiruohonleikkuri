import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import pandas as pd

st.set_page_config(page_title="Robottiruohonleikkuri", layout="wide")
st.title("🌿 Robottiruohonleikkurin simulaatio")

st.sidebar.header("🔧 Valitse toiminto")

tila = st.sidebar.radio("Valitse tila:", ("Luo kerta-analyysi", "Luo data-aineisto analyysia varten"))

# Yhteiset parametrit
pituus = st.sidebar.number_input("Alueen pituus (m)", min_value=1, value=10)
leveys = st.sidebar.number_input("Alueen leveys (m)", min_value=1, value=10)
leikkuusade = st.sidebar.number_input("Leikkuusäde (cm)", min_value=1, value=9)
nopeus_kmh = st.sidebar.number_input("Nopeus (km/h)", min_value=0.1, value=1.0)
leikkuuhalkaisija = 2 * leikkuusade / 100  # metreinä

def suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh, nopeutuskerroin=10, nayta_kuva=False, tallenna_data=False):
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

    data = []

    def merkitse_leikattu(x, y):
        cx = int(x / dx)
        cy = int(y / dx)
        r = int(leikkuuhalkaisija / (2 * dx))
        for i in range(max(0, cy - r), min(ny, cy + r)):
            for j in range(max(0, cx - r), min(nx, cx + r)):
                if np.hypot((j - cx), (i - cy)) * dx <= leikkuuhalkaisija / 2:
                    grid[i, j] = 1

    fig, ax = plt.subplots(figsize=(6, 6)) if nayta_kuva else (None, None)
    plot = st.empty() if nayta_kuva else None

    seuraava_raportointi = 0
    koko_ala = pituus * leveys

    while not np.all(grid == 1):
        x2 = x1 + askel_x
        y2 = y1 + askel_y

        if not (0 <= x2 <= leveys) or not (0 <= y2 <= pituus):
            suunta = np.random.rand() * 2 * np.pi
            askel_x = np.cos(suunta) * nopeus_mps * dt
            askel_y = np.sin(suunta) * nopeus_mps * dt
            x1 = np.clip(x2, 0, leveys)
            y1 = np.clip(y2, 0, pituus)
            kaannokset += 1
            continue

        px, py = x1, y1
        steps = int(np.hypot(x2 - x1, y2 - y1) / dx)
        for _ in range(steps):
            px += (x2 - x1) / steps
            py += (y2 - y1) / steps
            merkitse_leikattu(px, py)

        x1, y1 = x2, y2
        t += dt

        if tallenna_data and t >= seuraava_raportointi:
            leikattu_ala = np.sum(grid) * (dx ** 2)
            leikattu_pros = 100 * leikattu_ala / koko_ala
            leikkaamaton_pros = 100 - leikattu_pros
            data.append({
                "Aika (min)": t // 60,
                "Leikattu %": round(leikattu_pros, 2),
                "Leikkaamaton %": round(leikkaamaton_pros, 2),
                "Käännökset": kaannokset
            })
            seuraava_raportointi += 60

        if nayta_kuva and (np.sum(grid) % nopeutuskerroin == 0):
            ax.clear()
            ax.imshow(grid, extent=[0, leveys, 0, pituus], origin='lower', cmap='Greens', alpha=0.8)
            ax.set_xlim(0, leveys)
            ax.set_ylim(0, pituus)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f"Aika: {str(timedelta(seconds=t))}")
            plot.pyplot(fig)

    leikattu_ala = np.sum(grid) * (dx ** 2)
    return t, leikattu_ala, kaannokset, data

if tila == "Luo kerta-analyysi":
    nopeutuskerroin = st.sidebar.slider("Simulaation nopeutuskerroin", 1, 100, 30)
    if st.button("🚀 Käynnistä simulaatio"):
        st.subheader("Simulaatio käynnissä...")
        t, leikattu_ala, kaannokset, data = suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh, nopeutuskerroin, True, True)
        st.success("✅ Simulaatio valmis!")
        st.markdown(f"""
        - ⏱️ **Aikaa kului:** {str(timedelta(seconds=t))}
        - 🟩 **Leikattua pinta-alaa:** {leikattu_ala:.2f} m²
        - 🔁 **Käännöksiä:** {kaannokset}
        - ✂️ **Leikkuuhalkaisija:** {leikkuuhalkaisija:.2f} m
        """)

        df = pd.DataFrame(data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Lataa simulaation CSV-data",
            data=csv,
            file_name='kerta_analyysi_data.csv',
            mime='text/csv'
        )

elif tila == "Luo data-aineisto analyysia varten":
    n = st.sidebar.number_input("Simulaatioiden lukumäärä", min_value=1, value=10)
    if st.button("📊 Suorita analyysisimulaatiot"):
        tulokset = []
        st.subheader("Simulaatiot käynnissä...")
        for i in range(n):
            t, leikattu_ala, kaannokset, _ = suorita_simulaatio(pituus, leveys, leikkuuhalkaisija, nopeus_kmh)
            tulokset.append({
                "Simulaatio": i + 1,
                "Aika (s)": t,
                "Aika (hh:mm:ss)": str(timedelta(seconds=t)),
                "Leikattu ala (m²)": leikattu_ala,
                "Käännökset": kaannokset,
                "Leikkuuhalkaisija (m)": leikkuuhalkaisija,
                "Nopeus (km/h)": nopeus_kmh,
                "Alueen pinta-ala (m²)": pituus * leveys
            })

        df = pd.DataFrame(tulokset)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Lataa tulokset CSV-muodossa",
            data=csv,
            file_name='simulaatio_data.csv',
            mime='text/csv'
        )
