import xarray as xr
from progressbar import progressbar as bar
import numpy as np
import pandas as pd

import sys
from os import path, makedirs, listdir
from datetime import datetime
from utils.zbin import read_gzip_binary, write_gzip_binary
from utils.grid import Grid

# wrf files
input_dir = sys.argv[1]
observations_dir = sys.argv[2]
# risico input files
output_dir = sys.argv[3]
# list of input files
file_list_file = sys.argv[4]


makedirs(output_dir, exist_ok=True)
input_file_dir = path.dirname(file_list_file)
if input_file_dir != '':
    makedirs(input_file_dir, exist_ok=True)

var_names = {
 'T2': 'T',
 'U10': 'U',
 'V10': 'V',
 'RAINNC': 'P', 
 'Q2': 'R', 
 'PLUVIOMETRO_1h': 'O', 
 'TERMOMETRO_1h': 'K',
 'IGROMETRO_1h': 'F',    
 'PLUVIOMETRO_3h': 'O', 
 'TERMOMETRO_3h': 'K',
 'IGROMETRO_3h': 'F',    

}

wrf_dirs = list(filter(lambda d: not path.isfile(d), listdir(input_dir)))



with open(file_list_file, 'w') as file_list:
    for wrf_dir in wrf_dirs:
        wrf_run_dir = path.join(input_dir, wrf_dir)
        nc_files = list(map(
            lambda f: path.join(wrf_run_dir, f),
            sorted(list(filter(
                lambda s: s.startswith('auxhist'), listdir(wrf_run_dir)
        )))))

        last_p = 0

        for f in bar(nc_files):
            try:
                ds = xr.open_dataset(f)
                for var_name, var_risico in var_names.items():
                    if var_name in ds.variables:
                        values = ds[var_name].values

                        if var_risico == 'P':
                            last_p = values
                            values = values - last_p


                        lats = ds['XLAT'].values[0,:,:]
                        lons = ds['XLONG'].values[0,:,:]
                        min_lat, max_lat, min_lon, max_lon, n_rows, n_cols = lats[0,0], lats[-1,0], lons[0,0], lons[0,-1], lats.shape[0], lons.shape[1]
                        grid = Grid(lats, lons, regular=False)

                        date_str = ds.Times[0].values.tostring().decode("utf-8") 
                        date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
                        out_date_str = date.strftime('%Y%m%d%H%M')

                        out_file = f'{output_dir}/{out_date_str}_wrf_{var_risico}.zbin'
                        write_gzip_binary(out_file, values, grid)

                        file_list.write(path.abspath(out_file) + '\n')
            except Exception as e: print('exception', f, e)
            
    # observations
    nc_files = list(map(
        lambda f: path.join(observations_dir, f),
        sorted(list(filter(
            lambda s: s.endswith('.nc'), listdir(observations_dir)
    )))))
    for f in bar(nc_files):
        print(f)
        ds = xr.open_dataset(f)

        for var_name, var_risico in var_names.items():
            if var_name in ds.variables:
                lats = ds['latitude'].values[:,:]
                lons = ds['longitude'].values[:,:]
                min_lat, max_lat, min_lon, max_lon, n_rows, n_cols = lats[0,0], lats[-1,0], lons[0,0], lons[0,-1], lats.shape[0], lons.shape[1]
                grid = Grid(lats, lons, regular=False)

                for time in ds['time']:
                    date = datetime.utcfromtimestamp(time.values.tolist()/1e9)
                    pd.Timestamp(date).round('60min').to_pydatetime()
                    out_date_str = date.strftime('%Y%m%d%H%M')
                    values = ds[var_name].sel(time=time).values
                    values[values<-9999 | np.isnan(values)] = -9999
                    out_file = f'{output_dir}/{out_date_str}_observation_{var_risico}.zbin'
                    write_gzip_binary(out_file, values, grid)

                    file_list.write(path.abspath(out_file) + '\n')
                    
                    