import os
import sys

from from_root import from_root

p = from_root('CODE_OF_CONDUCT.md').parent
sys.path.insert(1, str(p))

from scrapers_library.data_portals.opendata.opendata_scraper_2 import opendata_scraper2

# Change to what you need (remove what you don't)
save_url = [
    [
        "crime_data/",
        "https://data.cityofnewyork.us/api/views/5uac-w243/rows.csv?accessType=DOWNLOAD",
    ],
    [
        "crime_data/historic",
        "https://data.cityofnewyork.us/api/views/57mv-nv28/rows.csv?accessType=DOWNLOAD",
    ],
]
save_folder = "./data/"

# Crawl-delay is 1, so no need to set it.
opendata_scraper2(save_url, save_folder, save_subfolder=True)