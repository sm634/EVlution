from model.model import *
import time 
import pandas as pd
import matplotlib.pyplot as plt


def run_model(name, CP_loc, N, t, discharge_rate):
    t1 = time.time()
    model = EVSpaceModel(CP_loc=CP_loc,N=N, discharge_rate=discharge_rate)
    model.run_model(t)  
    mdf = model.datacollector.get_model_vars_dataframe()
    adf = model.datacollector.get_agent_vars_dataframe()
    t2 = time.time()
    return t2-t1, mdf, adf

CP_loc_init = pd.read_csv('inputs\CP_locs.csv')
num_runs = 20
N = 500
discharge_rate = 0.1
t=50
res = []
for i in range(num_runs):
    CP_loc = CP_loc_init.copy()
    CP_loc['x'] = 5 + (CP_loc_init['x'] - 5) * i/num_runs/0.6
    CP_loc['y'] = 5 + (CP_loc_init['y'] - 5) * i/num_runs/0.6
    t_diff, mdf, adf = run_model(name=i, CP_loc=CP_loc,N=N, discharge_rate=discharge_rate, t=t)
    print(i, t_diff)
    x_dist = sum((CP_loc['x'] - 5)**2 + (CP_loc['y'] - 5)**2)**0.5
    res.append({'name':i,
                't': t_diff,
                'x_dist' : x_dist,
                'trips': mdf.completed_trip.sum()/t/N, 
                'dead_cars': mdf.dead_cars.sum()/t/N
                })

res_df = pd.DataFrame(res)

fig, axs = plt.subplots()
axs.plot(res_df['x_dist'],res_df['dead_cars'])
axs.set(ylabel='Average time as Dead Car', xlabel='Distance between CPs')
fig.show()