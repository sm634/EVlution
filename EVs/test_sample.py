from model.model import EVSpaceModel
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import seaborn as sns
import numpy as np



CP_loc='inputs\CP_locs.csv'
POI_file = 'inputs/POIs.csv'
speed = 0.3

model = EVSpaceModel()  #CP_loc=CP_loc,POIs=POI_file
model.run_model(1000) #24*365   