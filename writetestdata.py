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

	print(day)
	for j in ['matutinum', 'laudes+prima+tertia+sexta+nona', 'vesperae+completorium']:
		with open(f'testdata/{day}-{j.replace("+", "-")}.json', 'w') as fileout:
			fileout.write(datamanage.dump_data(breviarium.generate(root, day, j)))

