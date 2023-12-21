import numpy
import pandas

class FileLoader:
    path: str
    np: numpy.ndarray

    def __init__(self, path) -> None:
        self.path = path

    def load(self):
        df: pandas.DataFrame = pandas.read_csv(self.path)
        self.np = df.to_numpy()

