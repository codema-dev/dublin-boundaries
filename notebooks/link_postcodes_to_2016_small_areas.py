# %%
from os import path
from shutil import unpack_archive
from urllib.request import urlretrieve

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import box

data_dir = Path("../data")


# %%
def sjoin_center_inside(dfA, dfB):
    """ Join where center of A intersects B """
    dfA_center = dfA.copy()
    dfA_center.geometry = dfA.geometry.representative_point()
    dfA_sjoined = gpd.sjoin(dfA_center, dfB, op="intersects")
    return dfA_sjoined.assign(geometry=dfA.geometry)


# %% [markdown]
# # Get Dublin Boundary

# %%
dublin_boundary_filepath = "../data/dublin_boundary.geojson"
if not path.exists(dublin_boundary_filepath):
    urlretrieve(
        url="https://zenodo.org/record/4577018/files/dublin_boundary.geojson",
        filename=dublin_boundary_filepath,
    )

dublin_boundary = gpd.read_file(dublin_boundary_filepath, driver="GeoJSON").to_crs(
    epsg=2157
)


# %% [markdown]
# # Get 2016 Small Area Boundaries

# %%
small_area_boundaries_filepath = (
    "../data/Small_Areas_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015-shp"
)
if not path.exists(small_area_boundaries_filepath):
    urlretrieve(
        url="https://opendata.arcgis.com/datasets/c85e610da1464178a2cd84a88020c8e2_3.zip",
        filename=f"{small_area_boundaries_filepath}.zip",
    )
    unpack_archive(
        f"{small_area_boundaries_filepath}.zip",
        small_area_boundaries_filepath,
    )

small_area_boundaries = gpd.read_file(small_area_boundaries_filepath)[
    ["SMALL_AREA", "EDNAME", "geometry"]
].to_crs(epsg=2157)
dublin_small_area_boundaries = sjoin_center_inside(
    small_area_boundaries,
    dublin_boundary,
)


# %% [markdown]
# # Get Postcode boundaries

# %%
ireland_postcode_boundaries_filepath = (
    date_dir / "ireland_postcode_boundaries_autoaddress.geojson"
)
if not path.exists(dublin_postcode_boundaries_filepath):
    urlretrieve(
        url=(
            "https://www.autoaddress.ie/docs/default-source/default-document-library/routingkeys_shape_itm_2016_09_29.zip"
        ),
        filename=dublin_postcode_boundaries_filepath,
    )

dublin_postcode_boundaries = (
    gpd.read_file(dublin_postcode_boundaries_filepath, driver="GeoJSON")
    .to_crs(epsg=2157)
    .loc[:, ["postcodes", "local_authority", "geometry"]]
)

# %% [markdown]
# # Extract Small Areas within Dublin Postcode boundaries (some remain...)

# %%
small_areas_linked_to_dublin_postcodes = join.centroids_within(
    dublin_small_area_boundaries,
    dublin_postcode_boundaries,
)


# %% [markdown]
# # Link remaining Small Areas to Dublin Postcodes manually

# %%
missing_sas = dublin_small_area_boundaries.merge(
    most_small_areas_linked_to_dublin_postcodes, how="left", indicator=True
).query("`_merge` == 'left_only'")

# %%
f, ax = plt.subplots(figsize=(20, 20))
dublin_postcode_boundaries.plot(ax=ax, facecolor="none", edgecolor="r")
missing_sas.plot(ax=ax)
missing_sas.apply(
    lambda gdf: ax.annotate(
        text=gdf["SMALL_AREA"],
        xy=gdf.geometry.centroid.coords[0],
        font={"size": 3},
    ),
    axis=1,
)
dublin_boundary.plot(ax=ax, facecolor="none", edgecolor="black")
dublin_bounding_box.plot(ax=ax, facecolor="none", edgecolor="cyan")


# %%
missing_sas_linked = missing_sas.set_index("SMALL_AREA").copy()
co_dublin_sas = [
    "267123031",
    "267095019/267095021",
    "267065027/267065031",
    "267106008",
    "267075008",
    "267064003/267064004",
    "267095019/267095021",
    "267065027/267065031",
    "267106008",
    "267103003",
]
missing_sas_linked.loc[co_dublin_sas, "postcodes"] = "Co. Dublin"
dublin_18_sas = [
    "267120004",
    "267120009",
    "267120008",
    "267122003",
    "267122001",
    "267120005",
    "267122002",
    "267122017",
    "267122016",
    "267120006",
    "267120007",
]
missing_sas_linked.loc[dublin_18_sas, "postcodes"] = "Dublin 18"
fingal_sas = [
    "267123031",
    "267095019/267095021",
    "267065027/267065031",
    "267106008",
]
missing_sas_linked.loc[fingal_sas, "local_authority"] = "Fingal"
sd_sas = ["267103003"]
missing_sas_linked.loc[sd_sas, "local_authority"] = "South Dublin"
dlr_sas = [
    "267075008",
    "267064003/267064004",
    "267120004",
    "267120009",
    "267120008",
    "267122003",
    "267122001",
    "267120005",
    "267122002",
    "267122017",
    "267122016",
    "267120006",
    "267120007",
]
missing_sas_linked.loc[dlr_sas, "local_authority"] = "Dún Laoghaire-Rathdown"
missing_sas_linked = (
    missing_sas_linked.drop(columns="_merge").dropna(how="any").reset_index()
)

# %%
small_areas_linked_to_dublin_postcodes = pd.concat(
    [most_small_areas_linked_to_dublin_postcodes, missing_sas_linked]
)

# %% [markdown]
# # Inspect Small Areas to Postcodes Link

# %%
f, ax = plt.subplots(figsize=(20, 20))
small_areas_linked_to_dublin_postcodes.plot(ax=ax, column="postcodes")
dublin_postcode_boundaries.plot(ax=ax, facecolor="none", edgecolor="black")
dublin_postcode_boundaries.apply(
    lambda gdf: ax.annotate(
        text=gdf["postcodes"],
        xy=gdf.geometry.centroid.coords[0],
    ),
    axis=1,
)
dublin_boundary.plot(ax=ax, facecolor="none", edgecolor="black")
dublin_bounding_box.plot(ax=ax, facecolor="none", edgecolor="cyan")

# %% [markdown]
# # Save

# %%
small_areas_linked_to_dublin_postcodes.to_file(
    "../data/small_areas_boundaries_2016_linked_to_autoaddress_dublin_postcodes.geojson",
    driver="GeoJSON",
)
