from model.model import *
import time

cfgs = ['None', 'configs/Mississauga_cfg.yml', 'configs/Point_Edward_cfg.yml',
        'configs/east_box.yml', 'configs/west_box.yml']

print("The model agents will simulate across: ", cfgs)

start = time.time()
n_seeds = 4
n_hours = 9500

for cfg in cfgs:
    for seed in range(n_seeds):
        print(cfg, ": ", seed)
        model = EVSpaceModel(cfg=cfg, ModelP_seed=seed)
        model.run_model(9500)
        model.save()

end = time.time() - start
print(f"Minutes it took to run the simulation for {n_hours} "
      f"hours of agent steps and {n_seeds} complete seeds/trials: ", end/60)
