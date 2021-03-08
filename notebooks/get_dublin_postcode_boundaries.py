# %%
from os import path
from pathlib import Path
from shutil import unpack_archive
from urllib.request import urlretrieve

import geopandas as gpd

data_dir = Path("../data")

# %%
def sjoin_center_inside(dfA, dfB):
    """ Join where center of A intersects B """
    dfA_center = dfA.copy()
    dfA_center.geometry = dfA.geometry.representative_point()
    dfA_sjoined = gpd.sjoin(dfA_center, dfB, op="intersects")
    return dfA_sjoined.assign(geometry=dfA.geometry).drop(columns="index_right")


# %% [markdown]
# # Get Dublin Local Authority boundaries

dublin_admin_county_boundaries_filepath = (
    data_dir / "dublin_admin_county_boundaries.geojson"
)
if not path.exists(dublin_admin_county_boundaries_filepath):
    urlretrieve(
        url=(
            "https://zenodo.org/record/4576987/files/dublin_admin_county_boundaries.geojson"
        ),
        filename=dublin_admin_county_boundaries_filepath,
    )

dublin_admin_county_boundaries = (
    gpd.read_file(
        dublin_admin_county_boundaries_filepath,
    )
    .loc[:, ["COUNTYNAME", "geometry"]]
    .rename(columns={"COUNTYNAME": "local_authority"})
)

# %% [markdown]
# # Get Postcode boundaries

ireland_postcode_boundaries_filepath = (
    data_dir / "ireland_postcode_boundaries_autoaddress"
)
if not path.exists(ireland_postcode_boundaries_filepath):
    urlretrieve(
        url=(
            "https://www.autoaddress.ie/docs/default-source/default-document-library/routingkeys_shape_itm_2016_09_29.zip"
        ),
        filename=ireland_postcode_boundaries_filepath.with_suffix(".zip"),
    )
    unpack_archive(
        ireland_postcode_boundaries_filepath.with_suffix(".zip"),
        ireland_postcode_boundaries_filepath,
    )

ireland_postcode_boundaries = gpd.read_file(
    ireland_postcode_boundaries_filepath,
)


# %% [markdown]
# # Extract Dublin Postcode boundaries into it's corresponding Local Authority

dublin_postcode_boundaries = sjoin_center_inside(
    ireland_postcode_boundaries, dublin_admin_county_boundaries
).assign(
    CountyName=lambda gdf: gdf["Descriptor"]
    .str.title()
    .str.replace("^(?!Dublin.*).*", "Co. Dublin", regex=True)
)


# %% [markdown]
# # Save
dublin_postcode_boundaries.to_file(
    data_dir / "dublin_postcode_boundaries_autoaddress.geojson",
    driver="GeoJSON",
)
