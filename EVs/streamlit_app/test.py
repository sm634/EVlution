import requests
import svgpath2mpl, shapely.geometry, shapely.affinity
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import geopandas as gpd
import json
import numpy as np


# download maki icons
# https://github.com/mapbox/maki/tree/main/icons
f = Path.cwd().joinpath("maki")
if not f.is_dir():
    f.mkdir()
f = f.joinpath("maki.zip")
if not f.exists():
    r = requests.get("https://github.com/mapbox/maki/zipball/main")
    with open(f, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)

fz = ZipFile(f)
fz.extractall(f.parent)

def to_shapely(mpl, simplify=0):
    p = shapely.geometry.MultiPolygon([shapely.geometry.Polygon(a).simplify(simplify) for a in mpl])
    p = shapely.affinity.affine_transform(p,[1, 0, 0, -1, 0, 0],)
    p = shapely.affinity.affine_transform(p,[1, 0, 0, 1, -p.centroid.x, -p.centroid.y],)
    return p

# convert SVG icons to matplolib geometries and then into shapely geometries
# keep icons in dataframe for further access...
SIMPLIFY=.1
dfi = pd.concat(
    [
        pd.read_xml(sf).assign(
            name=sf.stem,
            mpl=lambda d: d["d"].apply(
                lambda p: svgpath2mpl.parse_path(p).to_polygons()
            ),
            shapely=lambda d: d["mpl"].apply(lambda p: to_shapely(p, simplify=SIMPLIFY)),
        )
        for sf in f.parent.glob("**/*.svg")
    ]
).set_index("name")

# build a geojson layer that can be used in plotly mapbox figure layout
def marker(df, marker="marker", size=1, color="green", lat=51.379997, lon=-0.406042):
    m = df.loc[marker, "shapely"]
    if isinstance(lat, float):
        gs = gpd.GeoSeries(
            [shapely.affinity.affine_transform(m, [size, 0, 0, size, lon, lat])]
        )
    elif isinstance(lat, (list, pd.Series, np.ndarray)):
        gs = gpd.GeoSeries(
            [
                shapely.affinity.affine_transform(m, [size, 0, 0, size, lonm, latm])
                for latm, lonm in zip(lat, lon)
            ]
        )
    return {"source":json.loads(gs.to_json()), "type":"fill", "color":color}

# display all icons to make sure they look ok...
gpd.GeoSeries(
    [
        shapely.affinity.affine_transform(
            s, [1, 0, 0, 1, (i % 20) * 20, (i // 20) * 20]
        )
        for i, s in enumerate(dfi["shapely"])
    ]
).plot()

dfi.loc["karaoke", "shapely"]