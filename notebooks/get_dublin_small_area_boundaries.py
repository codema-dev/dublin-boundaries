# %%
from pathlib import Path
from shutil import unpack_archive

import geopandas as gpd

from dublin_building_stock.download import download
from dublin_building_stock.get import get_dublin_small_area_boundaries
from dublin_building_stock.join import get_geometries_within
from dublin_building_stock.unzip import unzip_file

data_dir = Path("../data")

# %%
def sjoin_center_inside(dfA, dfB):
    """ Join where center of A intersects B """
    dfA_center = dfA.copy()
    dfA_center.geometry = dfA.geometry.representative_point()
    dfA_sjoined = gpd.sjoin(dfA_center, dfB, op="intersects")
    return dfA_sjoined.assign(geometry=dfA.geometry)


# %%
dublin_boundary_filepath = data_dir / "dublin_boundary.geojson"
download(
    "https://zenodo.org/record/4577018/files/dublin_boundary.geojson",
    dublin_boundary_filepath,
)
dublin_boundary = gpd.read_file(dublin_boundary_filepath, driver="GeoJSON")

# %%
ireland_small_area_boundaries_filepath = (
    data_dir
    / "Small_Areas_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015-shp"
)
download(
    "https://opendata.arcgis.com/datasets/c85e610da1464178a2cd84a88020c8e2_3.zip",
    ireland_small_area_boundaries_filepath.with_suffix(".zip"),
)
unzip_file(
    ireland_small_area_boundaries_filepath.with_suffix(".zip"),
    ireland_small_area_boundaries_filepath,
)
ireland_small_area_boundaries = gpd.read_file(ireland_small_area_boundaries_filepath)

# %%
dublin_small_area_boundaries = sjoin_center_inside(
    ireland_small_area_boundaries.to_crs(epsg=2157),
    dublin_boundary.to_crs(epsg=2157),
)
# %% [markdown]
# # Save

# %%
dublin_small_area_boundaries.to_file(
    data_dir / "dublin_small_area_boundaries_complete.geojson",
    driver="GeoJSON",
)

# %%
dublin_small_area_boundaries_tableau = (
    dublin_small_area_boundaries[["SMALL_AREA", "geometry"]]
    .assign(
        area_km2=lambda gdf: gdf.geometry.area * 10 ** -6,
    )
    .to_crs(epsg=4326)
)

dublin_small_area_boundaries_tableau.to_file(
    data_dir / "dublin_small_area_boundaries_tableau.geojson",
    driver="GeoJSON",
)

# %%
