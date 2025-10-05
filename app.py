import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import requests
import os
import matplotlib.pyplot as plt

# =========================
# CONFIG APP
# =========================
st.set_page_config(page_title="Análisis de Pasivos Ambientales", layout="wide")
st.title("🌍 Análisis de Pasivos Ambientales y Afectación Poblacional")

# =========================
# ENTRADAS DEL USUARIO
# =========================
pais = st.text_input("País:", "Perú")
ciudad = st.text_input("Ciudad:", "Cajamarca")

lat, lon = None, None

# Geocodificación automática con ciudad + país
if ciudad and pais:
    url = f"https://nominatim.openstreetmap.org/search?city={ciudad}&country={pais}&format=json"
    try:
        r = requests.get(url).json()
        if len(r) > 0:
            lat, lon = float(r[0]['lat']), float(r[0]['lon'])
    except:
        st.warning("⚠️ No se pudo geocodificar. Ingrese manualmente.")

# Entrada manual si no hay coords
if not lat or not lon:
    lat = st.number_input("Latitud", value=-7.163, format="%.6f")
    lon = st.number_input("Longitud", value=-78.500, format="%.6f")

radio = st.slider("Radio principal de afectación (km)", 1, 20, 5)

# =========================
# MAPA BASE
# =========================
m = folium.Map(location=[lat, lon], zoom_start=11)

# Marcador del pasivo ambiental principal
folium.Marker(
    [lat, lon],
    popup="Pasivo ambiental principal",
    icon=folium.Icon(color="black", icon="skull-crossbones", prefix="fa")
).add_to(m)

# Radios de aspersión (rápida y lenta)
folium.Circle([lat, lon], radius=radio*1000, color="red", fill=True, fill_opacity=0.2, popup="Afectación rápida").add_to(m)
folium.Circle([lat, lon], radius=radio*2000, color="orange", fill=True, fill_opacity=0.15, popup="Afectación lenta").add_to(m)

# =========================
# CENTROS POBLADOS
# =========================
centros_path = "data/centros.csv"
poblados_afectados = []

if os.path.exists(centros_path):
    centros = pd.read_csv(centros_path)
    for _, row in centros.iterrows():
        punto = Point(row['lon'], row['lat'])
        dist = punto.distance(Point(lon, lat)) * 111.32
        if dist <= radio*2:  # dentro del radio lento
            poblados_afectados.append({
                "Centro": row['nombre'],
                "Distancia (km)": round(dist,2),
                "Población actual": row.get("poblacion", 500),
                "Población hace 10 años": row.get("poblacion_pasada", 300)
            })
            folium.Marker(
                [row['lat'], row['lon']],
                popup=f"{row['nombre']} ({dist:.2f} km)",
                icon=folium.Icon(color="green", icon="home", prefix="fa")
            ).add_to(m)
    if poblados_afectados:
        df_poblados = pd.DataFrame(poblados_afectados)
        st.subheader("🏘 Comunidades / Centros poblados afectados")
        st.table(df_poblados)

        # =========================
        # GRÁFICO DE BARRAS - POBLACIÓN AFECTADA
        # =========================
        st.subheader("📊 Población afectada por comunidad")
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(df_poblados["Centro"], df_poblados["Población actual"], color="tomato")
        ax.set_ylabel("Población afectada")
        ax.set_xlabel("Centros poblados")
        ax.set_title("Comparación de población afectada")
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig)

        # =========================
        # EVOLUCIÓN HISTÓRICA
        # =========================
        st.subheader("📈 Evolución histórica de población afectada")
        year_diff = st.slider("Años atrás para comparar", 5, 30, 10)

        # Crear datos de comparación (simplificado)
        df_hist = pd.DataFrame({
            "Centro": df_poblados["Centro"],
            f"Hace {year_diff} años": df_poblados["Población hace 10 años"],  # usando columna de ejemplo
            "Actual": df_poblados["Población actual"]
        })

        fig3, ax3 = plt.subplots(figsize=(7,4))
        ax3.bar(df_hist["Centro"], df_hist[f"Hace {year_diff} años"], alpha=0.6, label=f"Hace {year_diff} años", color="gray")
        ax3.bar(df_hist["Centro"], df_hist["Actual"], alpha=0.8, label="Actual", color="red")
        ax3.set_ylabel("Población")
        ax3.set_title("Comparación histórica")
        ax3.legend()
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig3)

else:
    st.warning("⚠️ No se encontró 'data/centros.csv'.")

# =========================
# CENTROS MÉDICOS
# =========================
medicos_path = "data/medicos.csv"
medicos_afectados = []

if os.path.exists(medicos_path):
    medicos = pd.read_csv(medicos_path)
    for _, row in medicos.iterrows():
        punto = Point(row['lon'], row['lat'])
        dist = punto.distance(Point(lon, lat)) * 111.32
        if dist <= radio*2.5:
            medicos_afectados.append({
                "Centro médico": row['nombre'],
                "Tipo": row['tipo'],
                "Distancia (km)": round(dist,2)
            })
            folium.Marker(
                [row['lat'], row['lon']],
                popup=f"{row['nombre']} - {row['tipo']} ({dist:.2f} km)",
                icon=folium.Icon(color="blue", icon="plus-square", prefix="fa")
            ).add_to(m)
    if medicos_afectados:
        df_medicos = pd.DataFrame(medicos_afectados)
        st.subheader("🏥 Centros médicos cercanos")
        st.table(df_medicos)

        # =========================
        # GRÁFICO DE BARRAS - CENTROS MÉDICOS
        # =========================
        st.subheader("📊 Centros médicos disponibles según distancia")
        fig2, ax2 = plt.subplots(figsize=(6,4))
        ax2.bar(df_medicos["Centro médico"], df_medicos["Distancia (km)"], color="skyblue")
        ax2.set_ylabel("Distancia (km)")
        ax2.set_xlabel("Centros médicos")
        ax2.set_title("Distancias de centros médicos cercanos")
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig2)

else:
    st.warning("⚠️ No se encontró 'data/medicos.csv'.")

# =========================
# MANUALES SEGÚN TIPO DE PASIVO
# =========================
st.subheader("📚 Recursos / Manuales según tipo de pasivo")
links = {
    "Relaves Mineros": "https://www.minem.gob.pe/minem/archivos/manual_relaves.pdf",
    "Botaderos": "https://www.minem.gob.pe/minem/archivos/manual_botaderos.pdf",
    "Plantas abandonadas": "https://www.unep.org/resources/report/manual-remediacion-sitios-contaminados"
}
for tipo, url in links.items():
    st.markdown(f"- [{tipo}]({url})")

# =========================
# MOSTRAR MAPA
# =========================
st_map = st_folium(m, width=750, height=550)

st.success("✅ Análisis completado con gráficos de barras y evolución histórica.")
