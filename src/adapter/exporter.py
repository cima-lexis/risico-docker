from utils.zbin import read_gzip_binary
import sys
import xarray as xr
import os
from datetime import datetime
import numpy as np
from progressbar import ProgressBar as PB

# risico output folder
out_folder = sys.argv[1]
# netcdf output file
filename = sys.argv[2]

files = os.listdir(out_folder)
grid = None
outputs = {}

bar = PB()
for f in bar(files):
    if f.endswith('.zbin'):
        model, model_date, date_ref, variable = f.split('_')
        variable = variable.replace('.zbin','')

        if variable not in ['UMB', 'V', 'I', 'W', 'VPPF', 'IPPF']: continue

        if variable not in outputs:
            outputs[variable] = []

        if not grid:
            values, grid = read_gzip_binary(filename=out_folder+f, read_grid=True)
        else:
            values, _ = read_gzip_binary(filename=out_folder+f, read_grid=False)


        outputs[variable].append(dict(date=date_ref, values=values))


bar = PB()
ds = xr.Dataset()
for var in bar(outputs.keys()):
    output = sorted(outputs[var], key=lambda d:d['date'])
    data = np.stack([d['values']for d in output], axis=0)
    ds[var] = xr.DataArray(data=data,
                 dims=('time', 'latitude','longitude'), 
                 coords={
                    'time': [datetime.strptime(d['date'], '%Y%m%d%H%M') for d in output],
                    'longitude': grid.lons[0,:],
                    'latitude': grid.lats[:,0]
                 }
    )

print('creating dataset %s' % filename)
ds.to_netcdf(filename)