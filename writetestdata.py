from datetime import date, timedelta
import copy
import warnings

import datamanage
import prioritizer
import breviarium

year = 2001
root = 'breviarium-1888'

warnings.filterwarnings('ignore')
for i in range(0, 365):
	day = date(year, 1, 1) + timedelta(days=i)

	for j in ['matutinum+laudes+prima+tertia+sexta+nona', 'vesperae+completorium']:
		with open(f'testdata/{day}-vesperal.json' if 'vesperae' in j else f'testdata/{day}-diurnal.json', 'w') as fileout:
			fileout.write(breviarium.dump_data(breviarium.generate(root, day, j)))

