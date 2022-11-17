from model.model import *

cfgs = ['None', 'configs/Mississauga_cfg.yml', 'configs/Point_Edward_cfg.yml',
        'configs/east_box.yml', 'configs/west_box.yml']

for cfg in cfgs:
    for seed in range(4):
        model = EVSpaceModel(cfg=cfg, ModelP_seed=seed)
        model.run_model(9000)
        model.save()
