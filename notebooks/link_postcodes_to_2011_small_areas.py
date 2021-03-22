# %%
from os import path
from shutil import unpack_archive
from urllib.request import urlretrieve

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import box

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
# # Get 2011 Small Area Boundaries

# %%
small_area_boundaries_filepath = "../data/Census2011_Small_Areas_generalised20m"
if not path.exists(small_area_boundaries_filepath):
    urlretrieve(
        url="http://census.cso.ie/censusasp/saps/boundaries/Census2011_Small_Areas_generalised20m.zip",
        filename=f"{small_area_boundaries_filepath}.zip",
    )
    unpack_archive(
        f"{small_area_boundaries_filepath}.zip",
        small_area_boundaries_filepath,
    )

dublin_small_area_boundaries = gpd.read_file(small_area_boundaries_filepath)[
    ["SMALL_AREA", "EDNAME", "geometry"]
].to_crs(epsg=2157)


# %% [markdown]
# # Get Postcode boundaries

# %%
if not path.exists("../data/dublin_postcode_boundaries_autoaddress.geojson"):
    urlretrieve(
        url=(
            "https://zenodo.org/record/4564347/files/"
            "dublin_postcode_boundaries_autoaddress.geojson"
        ),
        filename="../data/dublin_postcode_boundaries_autoaddress.geojson",
    )

postcode_boundaries = (
    gpd.read_file(
        "../data/dublin_postcode_boundaries_autoaddress.geojson", driver="GeoJSON"
    )
    .to_crs(epsg=2157)
    .loc[:, ["postcodes", "local_authority", "geometry"]]
)

dublin_postcode_boundaries = join.centroids_within(
    postcode_boundaries,
    dublin_bounding_box,
)

# %% [markdown]
# # Extract Small Areas within Dublin Postcode boundaries (some remain...)

# %%
most_small_areas_linked_to_dublin_postcodes = join.centroids_within(
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
        font={"size": 5},
    ),
    axis=1,
)
dublin_boundary.plot(ax=ax, facecolor="none", edgecolor="black")
dublin_bounding_box.plot(ax=ax, facecolor="none", edgecolor="cyan")


# %%
missing_sas = missing_sas.set_index("SMALL_AREA")
co_dublin_sas = [
    "267064003/267064004",
    "267075008",
    "267095019/267095021",
    "267065027/267065031",
    "267106008",
    "267103003",
]
missing_sas.loc[co_dublin_sas, "postcodes"] = "Co. Dublin"
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
missing_sas.loc[dublin_18_sas, "postcodes"] = "Dublin 18"
fingal_sas = ["267095019/267095021", "267065027/267065031", "267106008"]
missing_sas.loc[fingal_sas, "local_authority"] = "Fingal"
sd_sas = ["267103003"]
missing_sas.loc[sd_sas, "local_authority"] = "South Dublin"
dlr_sas = [
    "267120004",
    "267120009",
    "267120008",
    "267122003",
    "267122001",
    "267064003/267064004",
    "267075008",
    "267120005",
    "267122002",
    "267122017",
    "267122016",
    "267120006",
    "267120007",
]
missing_sas.loc[dlr_sas, "local_authority"] = "Dún Laoghaire-Rathdown"
missing_sas = missing_sas.drop(columns="_merge").reset_index()

# %%
small_areas_linked_to_dublin_postcodes = pd.concat(
    [most_small_areas_linked_to_dublin_postcodes, missing_sas]
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
small_areas_linked_to_dublin_postcodes.to_csv(
    "../data/small_areas_boundaries_2011_linked_to_autoaddress_dublin_postcodes.csv",
    index=False,
)
