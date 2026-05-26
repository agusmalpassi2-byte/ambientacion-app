import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt

st.title("🌾 Ambientación automática")

archivo = st.file_uploader(
    "Subí un raster VARI/NDVI",
    type=["tif"]
)

if archivo:

    with rasterio.open(archivo) as src:
        raster = src.read(1)

    st.write("Raster cargado correctamente")

    fig, ax = plt.subplots()
    ax.imshow(raster)

    st.pyplot(fig)
