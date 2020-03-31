import pickle
from pickle import PickleError

import numpy as np
from scipy.interpolate import NearestNDInterpolator

from .utils import get_hash
from .grid_functions import to_grid_max, to_grid_min, to_grid_mean


class Grid:
    # static points and hash
    model_points = None
    model_points_hash = None

    regular = False
    lats = None
    lons = None
    grid_hash = None

    # grid association
    point_to_grid = None
    grid_to_point_i = None
    grid_to_point_idxs = None
    grid_to_point_np = None

    @staticmethod
    def set_model_points(xy):
        Grid.model_points = xy
        Grid.model_points_hash = get_hash(xy)

    @staticmethod
    def nan_values():
        return np.full(Grid.model_points.shape[0], np.nan, dtype='float32')

    @staticmethod
    def fill_values(value=0.0):
        return np.full(Grid.model_points.shape[0], value, dtype='float32')

    def __init__(self, lats=None, lons=None, regular=False):
        self.regular = regular
        self.lats = lats
        self.lons = lons

        self.grid_hash = get_hash(np.stack((self.lats, self.lons)))

    @staticmethod
    def regular(min_lat, max_lat, min_lon, max_lon, n_rows, n_cols):
        lats_r = np.linspace(min_lat, max_lat, n_rows)
        lons_r = np.linspace(min_lon, max_lon, n_cols)
        lons, lats = np.meshgrid(lons_r, lats_r)

        g = Grid(lats=lats, lons=lons, regular=True)

        return g

    def __build_cache(self):

        assert Grid.model_points is not None, 'set model points before using this function. Grid.set_model_points'

        # builds the cache if it is not ready
        grid_file = Grid.model_points_hash + '_' + self.grid_hash + '.p'
        try:
            # read the file
            self.point_to_grid, self.grid_to_point_i, self.grid_to_point_idxs, self.grid_to_point_np = pickle.load(open(grid_file, 'rb'))
        except (FileNotFoundError, PickleError):
            print('build grid cache')
            interp = NearestNDInterpolator((self.lons.ravel(), self.lats.ravel()), np.arange(0, self.lats.size))
            self.point_to_grid = interp(Grid.model_points).astype('int32')
            self.grid_to_point_i = np.unique(self.point_to_grid).astype('int32')
            self.grid_to_point_np = np.zeros_like(self.grid_to_point_i, dtype='int32')
            grid_to_point_idxs = []
            max_len = 0
            for r, i in enumerate(self.grid_to_point_i):
                idxs = np.where(self.point_to_grid == i)[0]
                grid_to_point_idxs.append(idxs)
                max_len = max(max_len, len(idxs))
                self.grid_to_point_np[r] = len(idxs)
            self.grid_to_point_idxs = np.zeros((len(self.grid_to_point_i), max_len), dtype='int32')
            for r, idxs in enumerate(grid_to_point_idxs):
                self.grid_to_point_idxs[r, 0:len(idxs)] = idxs

            # save file
            pickle.dump((self.point_to_grid, self.grid_to_point_i, self.grid_to_point_idxs, self.grid_to_point_np), open(grid_file, "wb"))

    def get_values(self, values):
        if self.point_to_grid is None:
            self.__build_cache()

        return values.ravel()[self.point_to_grid]

    #@timeit
    def values_to_grid(self, values, method='mean'):
        """
        returns model points values on this grid
        :param values:
        :return:
        """
        if self.grid_to_point_i is None:
            self.__build_cache()

        output_values = np.full(self.lats.shape, np.nan, dtype='float32')
        output_linear = output_values.ravel()

        if method == 'max' or method == 'MAX':
            to_grid_max(self.grid_to_point_i.astype('int32'),
                         self.grid_to_point_np.astype('int32'),
                         self.grid_to_point_idxs.astype('int32'),
                         values, output_linear)

        elif method == 'min' or method == 'MIN':
            to_grid_min(self.grid_to_point_i.astype('int32'),
                         self.grid_to_point_np.astype('int32'),
                         self.grid_to_point_idxs.astype('int32'),
                         values, output_linear)

        elif method == 'mean' or method == 'MEAN':
            to_grid_mean(self.grid_to_point_i.astype('int32'),
                 self.grid_to_point_np.astype('int32'),
                 self.grid_to_point_idxs.astype('int32'),
                 values, output_linear)
        else:
            to_grid_mean(self.grid_to_point_i.astype('int32'),
                         self.grid_to_point_np.astype('int32'),
                         self.grid_to_point_idxs.astype('int32'),
                         values, output_linear)

        return output_values

