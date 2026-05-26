import tkinter as tk
from tkinter import filedialog, messagebox
import rasterio
import numpy as np
from sklearn.cluster import KMeans
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape
import matplotlib.pyplot as plt

# -------------------------
# FUNCION PRINCIPAL
# -------------------------
def procesar():

    file_path = filedialog.askopenfilename(filetypes=[("GeoTIFF", "*.tif")])

    if not file_path:
        return

    K = int(var_k.get())

    with rasterio.open(file_path) as src:
        raster = src.read(1)
        transform = src.transform
        crs = src.crs

    raster = np.nan_to_num(raster)
    flat = raster.reshape(-1, 1)

    flat = (flat - flat.min()) / (flat.max() - flat.min())

    kmeans = KMeans(n_clusters=K, n_init=10, random_state=42)
    labels = kmeans.fit_predict(flat)

    classified = labels.reshape(raster.shape)

    # -------------------------
    # VECTORIZAR
    # -------------------------
    geoms = []
    for geom, val in shapes(classified.astype(np.int32), transform=transform):
        geoms.append({
            "geometry": shape(geom),
            "properties": {"class": int(val)}
        })

    gdf = gpd.GeoDataFrame.from_features(geoms, crs=crs)

    # limpiar ruido
    gdf["area"] = gdf.geometry.area
    gdf = gdf[gdf["area"] > gdf["area"].quantile(0.1)]

    # exportar
    out_shp = file_path.replace(".tif", "_ambientes.shp")
    out_geo = file_path.replace(".tif", "_ambientes.geojson")

    gdf.to_file(out_shp)
    gdf.to_file(out_geo, driver="GeoJSON")

    messagebox.showinfo("Listo", "Ambientes generados correctamente")


# -------------------------
# INTERFAZ
# -------------------------
root = tk.Tk()
root.title("Ambientación automática")
root.geometry("300x150")

tk.Label(root, text="Ambientes (3-5)").pack()

var_k = tk.StringVar(value="4")
tk.Entry(root, textvariable=var_k).pack()

tk.Button(root, text="Procesar VARI/NDVI", command=procesar).pack(pady=20)

root.mainloop()