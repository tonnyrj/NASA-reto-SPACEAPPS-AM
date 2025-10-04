import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point

st.title("🌍 Análisis de Pasivos Ambientales y Afectación Poblacional")

# --- Entradas del usuario ---
pais = st.text_input("País:", "Perú")
ciudad = st.text_input("Ciudad:", "Cajamarca")
lat = st.number_input("Latitud", value=-7.163)
lon = st.number_input("Longitud", value=-78.5)
radio = st.slider("Radio de afectación (km)", 1, 20, 5)
anios = st.slider("Años para análisis histórico", 5, 50, 20)

st.write(f"📍 Ubicación: {ciudad}, {pais}")
st.write(f"🌐 Coordenadas: {lat}, {lon}")
st.write(f"📏 Radio de afectación: {radio} km")

# --- Mapa con Folium ---
m = folium.Map(location=[lat, lon], zoom_start=11)

# Marcador del pasivo ambiental
folium.Marker(
    [lat, lon],
    popup="Pasivo Ambiental",
    icon=folium.Icon(color="red", icon="industry", prefix="fa")
).add_to(m)

# Círculo de afectación
folium.Circle(
    [lat, lon], radius=radio*1000,
    color="blue", fill=True, fill_opacity=0.2,
    popup="Área de afectación"
).add_to(m)

# Mostrar mapa en Streamlit
st_map = st_folium(m, width=700, height=500)

# --- Simulación de población afectada ---
# Aquí deberías cargar datos raster reales (ej: NASA SEDAC GPWv4)
poblacion_afectada = int(np.random.randint(5000, 50000))
st.metric("👥 Personas afectadas (estimado)", poblacion_afectada)

# --- Evolución histórica del daño ambiental ---
años = np.arange(anios+1)
afectados_historico = np.linspace(poblacion_afectada*0.3, poblacion_afectada, anios+1)

fig, ax = plt.subplots()
ax.plot(años, afectados_historico, marker="o", color="red", label="Personas afectadas")
ax.axhline(y=poblacion_afectada, color="black", linestyle="--", label="Situación actual")
ax.set_title(f"Evolución del daño ambiental en los últimos {anios} años")
ax.set_xlabel("Años atrás")
ax.set_ylabel("Personas afectadas (estimado)")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)
st.pyplot(fig)

st.success("✅ Análisis completado. Resultados generados con base en datos simulados.")
