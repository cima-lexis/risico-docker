import gzip
import struct

import numpy as np

from .grid import Grid


def read_gzip_binary(filename, nan_value=-9999.0, read_grid=True):
    with gzip.open(filename, "rb") as zf:

        grid_type = struct.unpack('i', zf.read(4))[0]
        n_rows, n_cols = struct.unpack('i' * 2, zf.read(4 * 2))
        n_values = n_rows * n_cols

        grid = None
        if read_grid:
            if grid_type == 1:
                # regular grid
                lats = struct.unpack('f'*2, zf.read(4*2))
                lons = struct.unpack('f'*2, zf.read(4*2))
                #lats_r = np.linspace(lats[0], lats[1], n_rows).astype('float32')
                #lons_r = np.linspace(lons[0], lons[1], n_cols).astype('float32')
                #lons_arr, lats_arr = np.meshgrid(lons_r, lats_r)
                grid = Grid.regular(lats[0], lats[1], lons[0], lons[1], n_rows, n_cols)

            if grid_type == 0:
                #irregular grid
                lats = struct.unpack('f'*n_values, zf.read(4*n_values))
                lons = struct.unpack('f'*n_values, zf.read(4*n_values))
                lats_arr = np.reshape(np.array(lats), (n_rows, n_cols)).astype('float32')
                lons_arr = np.reshape(np.array(lons), (n_rows, n_cols)).astype('float32')
                grid = Grid(lats_arr, lons_arr)
        else:
            # skip the bytes for the grid
            bytes_to_seek = 2*2*4 if grid_type == 1 else 2*4*n_values
            zf.seek(bytes_to_seek, 1)

        values_vect = np.array(struct.unpack('f'*n_values, zf.read(4*n_values)), dtype='float32')
        values_vect[values_vect <= nan_value] = np.NaN
        vals = np.reshape(values_vect, (n_rows, n_cols))

        return vals, grid


def write_gzip_binary(filename, values, grid, nan_value=-9999.0):

    values = values.copy()
    values[np.isnan(values)] = nan_value

    with gzip.open(filename, "wb") as zf:
        zf.write(struct.pack('i', 1 if grid.regular else 0))
        n_rows = grid.lats.shape[0]
        n_cols = grid.lons.shape[1]
        n_values = n_rows * n_cols

        zf.write(struct.pack('i' * 2, n_rows, n_cols))

        if grid.regular:
            # regular grid
            zf.write(struct.pack('f'*2, grid.lats[0, 0], grid.lats[-1, 0]))
            zf.write(struct.pack('f'*2, grid.lons[0, 0], grid.lons[0, -1]))
        else:
            #irregular grid
            zf.write(struct.pack('f'*n_values, *grid.lats.flat))
            zf.write(struct.pack('f'*n_values, *grid.lons.flat))

        zf.write(struct.pack('f' * n_values, *values.flat))


if __name__ == '__main__':
    pass