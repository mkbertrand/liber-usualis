from datetime import date, timedelta
import time
import copy
import warnings
import os

import datamanage
import prioritizer
import breviarium

year = 2001
book = datamanage.get_book('breviarium-1888')

if not os.path.isdir('testdata'):
	os.makedirs('testdata')

start = time.time()
warnings.filterwarnings('ignore')
for i in range(0, 365):
	day = date(year, 1, 1) + timedelta(days=i)

	print(day)
	for j in ['matutinum', 'laudes+prima+tertia+sexta+nona', 'vesperae+completorium']:
		with open(f'testdata/{day}-{j.replace("+", "-")}.json', 'w') as fileout:
			fileout.write(datamanage.dump_data(breviarium.generate(book, day, j)))

print(f'Finished writing test date ({round(time.time() - start, 3)}s)')
