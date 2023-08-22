import os
import sys

import configs_annual as configs
from from_root import from_root

p = from_root('CODE_OF_CONDUCT.md').parent
sys.path.insert(1, str(p))

from utils.pdf.list_pdf_scrapers import list_pdf_v2

save_dir = "./data/"

list_pdf_v2(configs, save_dir, name_in_url=False, configs_file=True)