"""
This file contains a class that helps post-process libE optimization
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class PostProcOptimization(object):

    def __init__(self, path):
        """
        Initialize a postprocessing object

        Parameter:
        ----------
        path: string
            Path to the folder that contains the libE optimization
        """
        # Find the `npy` file that contains the results
        output_files = [ filename for filename in os.listdir(path) \
                    if filename.startswith('libE_history_for_run_')
                   and filename.endswith('.npy')]
        assert len(output_files) == 1

        # Load the file as a pandas DataFrame
        x  = np.load( os.path.join(path, output_files[0]) )
        d = { label: x[label].flatten() for label in x.dtype.names \
                if label not in ['x', 'x_on_cube'] }
        self.df = pd.DataFrame(d)

        # Only keep the simulations that finished properly
        self.df = self.df[self.df.returned]

        # Make the time relative to the start of the simulation
        self.df['given_time'] -= self.df['gen_time'].min()
        self.df['gen_time'] -= self.df['gen_time'].min()

    def get_df(self):
        """
        Return a pandas DataFrame containing the data from the simulation
        """
        return self.df

    def plot_optimization(self, resolution_parameter=None, **kwargs):
        """
        Plot the values that where reached during the optimization

        Parameters:
        -----------
        resolution_parameter: string or None
            Name of the resolution parameter
            If given, the different resolution will
            be plotted in different colors

        kwargs: optional arguments to pass to `plt.scatter`
        """
        if resolution_parameter is not None:
            resolution = self.df[resolution_parameter]
        else:
            resolution = None
        plt.scatter( self.df.given_time, self.df.f, c=resolution )

    def get_trace(self, resolution_parameter=None,
                   min_resolution=None, t_array=None,
                   plot=False, **kw):
        """
        Plot the minimum so far, as a function of time during the optimization

        Parameters:
        -----------
        resolution_parameter: string
            Name of the resolution parameter. If `resolution_parameter`
            and `min_resolution` are set, only the runs with resolution
            above `min_resolution` are considered.

        resolution_min: float
            Minimum resolution above which points are considered

        t_array: 1D numpy array
            If provided, th

        plot: bool
            Whether to plot the trace

        kw: extra arguments to the plt.plot function

        Returns:
        --------
        time, max
        """
        if resolution_parameter is not None:
            assert min_resolution is not None
            df = self.df[self.df[resolution_parameter]>min_resolution]
        else:
            df = self.df.copy()

        t = df.given_time.values
        cummin = df.f.cummin().values

        if t_array is not None:
            # Interpolate the trace curve on t_array
            N_interp = len(t_array)
            N_ref = len(t)
            cummin_array = np.zeros_like(t_array)
            i_ref = 0
            for i_interp in range(N_interp):
                while i_ref < N_ref-1 and t[i_ref+1] < t_array[i_interp]:
                    i_ref += 1
                cummin_array[i_interp] = cummin[i_ref]
        else:
            t_array = t
            cummin_array = cummin

        if plot:
            plt.plot( t_array, cummin_array, **kw )

        return t_array, cummin_array
