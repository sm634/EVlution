from model.model import *
import time
import pandas as pd
import matplotlib.pyplot as plt

cfgs = ['None', 'configs/Mississauga_cfg.yml', 'configs/Point_Edward_cfg.yml',
        'configs/east_box.yml', 'configs/west_box.yml']

for cfg in cfgs:
    for seed in range(4):
        print(cfg)
        model = EVSpaceModel(cfg=cfg, ModelP_seed=seed)
        print(model.model_name)
        model.run_model(1000)
        model.save()
