import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random

st.title(\"🌱 Robottiruohonleikkurin simulaatio\")

# Käyttäjän syötteet
radius_cm = st.number_input(\"Leikkuusäde (cm)\", min_value=1, max_value=100, value=18)
speed_kmh = st.number_input(\"Nopeus (km/h)\", min_value=0.1, max_value=10.0, value=1.0)
width_m = st.number_input(\"Alueen leveys (m)\", min_value=1, max_value=100, value=10)
height_m = st.number_input(\"Alueen pituus (m)\", min_value=1, max_value=100, value=10)
speedup = st.slider(\"Simulaation nopeutuskerroin\", min_value=1, max_value=100, value=20)

start = st.button(\"Käynnistä simulaatio\")

if start:
    st.subheader(\"🔄 Simulointi käynnissä...\")
    fig, ax = plt.subplots()

    cell_size = 5  # 1 metri = 5 pikseliä
    grid_w = int(width_m * cell_size)
    grid_h = int(height_m * cell_size)
    grid = np.zeros((grid_h, grid_w), dtype=bool)

    total_cells = grid_w * grid_h
    cut_cells = 0
    radius_px = int((radius_cm / 100) * cell_size)

    x, y = random.randint(0, grid_w - 1), random.randint(0, grid_h - 1)

    plot = st.pyplot(fig)
    start_time = time.time()

    while cut_cells < total_cells:
        dx = random.randint(-radius_px, radius_px)
        dy = random.randint(-radius_px, radius_px)
        x = max(0, min(x + dx, grid_w - 1))
        y = max(0, min(y + dy, grid_h - 1))

        for i in range(-radius_px, radius_px):
            for j in range(-radius_px, radius_px):
                xi = x + i
                yj = y + j
                if 0 <= xi < grid_w and 0 <= yj < grid_h:
                    if not grid[yj, xi]:
                        grid[yj, xi] = True
                        cut_cells += 1

        if random.random() < 0.1:  # päivitä kuva harvemmin suorituskyvyn vuoksi
            ax.clear()
            ax.imshow(grid, cmap=\"Greens\", origin=\"lower\")
            ax.set_title(\"Leikattu alue\")  
            ax.axis(\"off\")
            plot.pyplot(fig)

        time.sleep(0.01 / speedup)

    duration = time.time() - start_time
    st.success(\"🌟 Simulaatio valmis!\")
    st.markdown(f\"**Kesto (simuloituna):** {duration:.2f} s\")\n    st.markdown(f\"**Leikattu pinta-ala:** {width_m * height_m:.2f} m²\")\n    st.markdown(f\"**Leikkuusäde:** {radius_cm} cm\")\n    st.markdown(f\"**Nopeus:** {speed_kmh} km/h\")
