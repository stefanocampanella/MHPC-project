import numpy as np


class RMSE:
    """
    Root mean square error, with optional normalization
    """

    def __init__(self, observations, norm=None):

        self.observations = observations

        if norm == 'range':
            self.norm = observations.max() - observations.min()
        elif norm == 'square':
            self.norm = (observations * observations).mean()
        else:
            self.norm = 1.0

    def __call__(self, simulation):

        diff = self.observations - simulation
        rmse = np.sqrt((diff * diff).mean())

        return rmse / self.norm


class NSE:
    """
    Nash-Sutcliffe Efficiency
    """

    def __init__(self, observations):
        self.observations = observations
        self.square_mean = (observations * observations).mean()

    def __call__(self, simulation):
        diff = self.observations - simulation
        return np.sqrt((diff * diff).mean() / self.square_mean)


class KGE:
    """
    Kling-Gupta Efficiency
    """

    def __init__(self, observations):
        self.observations = observations
        self.mean = observations.mean()
        self.std = observations.std()

    def __call__(self, simulation):
        r = self.observations.corr(simulation) - 1
        m = simulation.mean() / self.mean - 1
        v = simulation.std() / self.std - 1

        return np.sqrt(r * r + m * m + v * v)
