import numpy as np
try:
    #raise ImportError
    import pyximport; pyximport.install(setup_args={'include_dirs': np.get_include()})
    from risico.utils.cython_functions import to_grid_max, to_grid_min, to_grid_mean

except ImportError as err:

    def to_grid_mean(
            gtp_i,
            gtp_len,
            gtp_idxs,
            values,
            out):

            for r in range(len(gtp_i)):
                i = gtp_i[r]
                l = gtp_len[r]

                if l == 1:
                    out[i] = values[gtp_idxs[r, 0]]
                else:
                    idxs = gtp_idxs[r, 0:l]
                    val = 0.0
                    count = 0
                    for idx in idxs:
                        cval = values[idx]
                        if not np.isnan(cval):
                            val = val + cval
                            count += 1

                    if count > 0:
                        val = val/count

                    out[i] = val

    def to_grid_max(
            gtp_i,
            gtp_len,
            gtp_idxs,
            values,
            out):

            for r in range(len(gtp_i)):
                i = gtp_i[r]
                l = gtp_len[r]
                if l == 1:
                    out[i] = values[gtp_idxs[r, 0]]
                else:
                    idxs = gtp_idxs[r, 0:l]
                    val = np.nan
                    for idx in idxs:
                        cval = values[idx]

                        if not np.isnan(cval):
                            if np.isnan(val):
                                val = cval
                            else:
                                val = max(val, cval)

                    out[i] = val

    def to_grid_min(
            gtp_i,
            gtp_len,
            gtp_idxs,
            values,
            out):

            for r in range(len(gtp_i)):
                i = gtp_i[r]
                l = gtp_len[r]
                if l == 1:
                    out[i] = values[gtp_idxs[r, 0]]
                else:
                    idxs = gtp_idxs[r, 0:l]
                    val = np.nan

                    for idx in idxs:
                        cval = values[idx]

                        if not np.isnan(cval):
                            if np.isnan(val):
                                val = cval
                            else:
                                val = min(val, cval)
                    out[i] = val