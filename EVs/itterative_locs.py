from model.model import *
import time 
import pandas as pd
import matplotlib.pyplot as plt

cfgs = ['None', 'configs/Mississauga_cfg.yml', 'configs/Point_Edward_cfg.yml',
        'configs/east_box.yml',  'configs/west_box.yml', 'configs/Bounding_box_1_config.yml']

for cfg in cfgs:
    for seed in range(10):
        print(cfg)
        model = EVSpaceModel(cfg = cfg,seed=seed)  
        model.run_model(240) #Change back later to 2400
        model.save()
