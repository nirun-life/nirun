#  Copyright (c) 2024 NSTDA
from translate_po.main import run

# move po file into /untranslated directory then run this file to see the magic!!
run(fro="en", to="th", src="untranslated", dest="translated")
