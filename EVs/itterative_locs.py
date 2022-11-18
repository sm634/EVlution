from model.model import *
import timeit

cfgs = ['None', 'configs/Mississauga_cfg.yml', 'configs/Point_Edward_cfg.yml',
        'configs/east_box.yml', 'configs/west_box.yml']

start = timeit.timeit()

for cfg in cfgs:
    for seed in range(4):
        print(cfg, ": ", seed)
        model = EVSpaceModel(cfg=cfg, ModelP_seed=seed)
        model.run_model(9000)
        model.save()

end = timeit.timeit() - start
print("Time it took to run: ", end)