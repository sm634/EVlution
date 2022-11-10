from model.model import *
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import seaborn as sns

model = EVSpaceModel(CP_loc='inputs\CP_locs.csv',discharge_rate=0.1,N=1000,grid_spacing=20)
model.run_model(100)   

print(model.datacollector.get_model_vars_dataframe())
print(model.datacollector.get_agent_vars_dataframe().tail())
print(model.datacollector_CP.get_agent_vars_dataframe().tail())
print(model.datacollector_gridpoints.get_agent_vars_dataframe().tail())

GP = model.datacollector_gridpoints.get_agent_vars_dataframe()
# XY = pd.DataFrame(GP['pos'].tolist()).rename({0:'X',1:'Y'},axis=1)



fig, ax = plt.subplots()
cs = ax.contourf(Z['X'], Z['Y'], Z['cars_passing'], locator=ticker.LogLocator(), cmap=cm.PuBu_r)

Z = GP.reset_index().groupby('AgentID').agg({'cars_passing':sum,'X':'first','Y':'first'})
sns.scatterplot(data=Z, x='X',y='Y',c='cars_passing')
