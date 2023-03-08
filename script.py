from amplpy import AMPL, Environment
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import os
import sys

#check for arguments
if len(sys.argv) < 2:
    print("Usage: python script.py 'path_to_ampl'")
    sys.exit(1)
else:
    path_to_ampl = sys.argv[1]

data_name = 'wf02_cb01_capex'
    

def plot_cable_layout(x_pd, pos, deterministic_cost=None, name='cable_layout.png'):
    size = (1+np.sqrt(1+4*len(x_pd)))/2
    size = int(size)
    G2 = nx.Graph()
    for i in range(len(x_pd)):
        if int(x_pd.iloc[i][0])==1:
            idx_1 = int(x_pd.index[i][0]) - 1
            idx_2 = int(x_pd.index[i][1]) - 1
            cableType = int(x_pd.index[i][2])
            G2.add_edge(idx_1, idx_2, color='C'+str(cableType-1))


    #figure with legend
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for cableType in range(1,4):
        ax.scatter([], [], c='C'+str(cableType-1), label='cable type '+str(cableType))


    #plot matrix as a graph with color
    nx.draw_networkx(G2, pos=pos, with_labels=True, edge_color=[G2[u][v]['color'] for u,v in G2.edges()], ax=ax)

    #add title
    if deterministic_cost is not None:
        plt.title('Cable layout with deterministic cost: '+str(deterministic_cost))

    plt.legend()
    #tight layout
    plt.tight_layout()
    #save figure
    plt.savefig(name)

#transform path_to_ampl as raw string
path_to_ampl = r'{}'.format(path_to_ampl)
ampl = AMPL(Environment(path_to_ampl))
ampl.reset()

ampl.read('cable_optimization_stochastic.mod')
ampl.readData(data_name+'.dat')

#get set VxW
VxW_pd = ampl.getSet('VxW').getValues().toPandas()

#normal distribution for each node in V and each scenario in W truncated between -0.5 and 0.5
P_deviation_pd = pd.DataFrame(np.random.normal(0, 0.5, len(VxW_pd)), index=VxW_pd.index)
P_deviation_pd = P_deviation_pd.clip(lower=-0.5, upper=0.5)

ampl.getParameter('P_deviation').setValues(P_deviation_pd)

ampl.setOption('solver', 'cplex')
ampl.setOption('cplex_options', 'timelimit=3600 iisfind 1')

####################### Results with deterministic solution
print('')
print('Results with deterministic solution')
print('')

#load deterministic solution from csv
solution_path = 'deterministic_solution_'+data_name+'.csv'
if os.path.isfile(solution_path):
    x_pd = ampl.getVariable('x').getValues().toPandas()
    index_x_pd = x_pd.index
    index_x_pd = x_pd.index
    x_pd = pd.read_csv(solution_path, index_col=0)
    x_pd.index = index_x_pd
    # set values of ampl variable x
    ampl.getVariable('x').setValues(x_pd)
    ampl.getVariable('x').fix()
else:
    print('No deterministic solution found. Please run deterministic optimization first.')
    exit()

ampl.solve()

print('New cables:', ampl.getVariable('new_cables').getValues().toPandas())
print('P_min:', ampl.getParameter('P_min').getValues().toPandas())

deterministic_cost = ampl.getVariable('deterministic_cost').getValues().toPandas().iloc[0][0]
deterministic_cost_readable = '{:,.2f}'.format(deterministic_cost)
print('Deterministic cost: ', deterministic_cost_readable)
stochastic_cost = ampl.getVariable('stochastic_cost').getValues().toPandas().iloc[0][0]
stochastic_cost_readable = '{:,.2f}'.format(stochastic_cost)
print('Stochastic cost: ', stochastic_cost_readable)
stochastic_cost_pessimistic = ampl.getVariable('stochastic_cost_pessimistic').getValues().toPandas().iloc[0][0]
stochastic_cost_pessimistic_readable = '{:,.2f}'.format(stochastic_cost_pessimistic)
print('Pessimistic stochastic cost: ', stochastic_cost_pessimistic_readable)
#log in txt.file
with open('results.txt', 'a') as f:
    f.write('Results with deterministic solution'+'\n')
    f.write('New cables: '+str(ampl.getVariable('new_cables').getValues().toPandas())+'\n')
    f.write('P_min: '+str(ampl.getParameter('P_min').getValues().toPandas())+'\n')
    f.write('Deterministic cost: '+str(deterministic_cost_readable)+'\n')
    f.write('Stochastic cost: '+str(stochastic_cost_readable)+'\n')
    f.write('Pessimistic stochastic cost: '+str(stochastic_cost_pessimistic_readable)+'\n')
    f.write(''+'\n')


#pos of nodes from ampl param x_coord y_coord
x_coord = ampl.getParameter('x_coord').getValues().toPandas()
y_coord = ampl.getParameter('y_coord').getValues().toPandas()
pos = {}
for i in range(len(x_coord)):
    pos[i] = (x_coord.iloc[i][0], y_coord.iloc[i][0])

x_pd = ampl.getVariable('x').getValues().toPandas()

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "deterministic_solution_cable_routing.png")

####################### Results with tradeoff solution
print('')
print('Results with tradeoff solution')
print('')

ampl.getVariable('x').unfix()

#deterministic cost weight of 0.8
ampl.getParameter('deterministic_cost_weight').set(0.8)

#stochastic cost weight of 0.2
ampl.getParameter('stochastic_cost_weight').set(0.2)

ampl.solve()

print('New cables:', ampl.getVariable('new_cables').getValues().toPandas())
print('P_min:', ampl.getParameter('P_min').getValues().toPandas())

deterministic_cost = ampl.getVariable('deterministic_cost').getValues().toPandas().iloc[0][0]
deterministic_cost_readable = '{:,.2f}'.format(deterministic_cost)
print('Deterministic cost: ', deterministic_cost_readable)
stochastic_cost = ampl.getVariable('stochastic_cost').getValues().toPandas().iloc[0][0]
stochastic_cost_readable = '{:,.2f}'.format(stochastic_cost)
print('Stochastic cost: ', stochastic_cost_readable)
stochastic_cost_pessimistic = ampl.getVariable('stochastic_cost_pessimistic').getValues().toPandas().iloc[0][0]
stochastic_cost_pessimistic_readable = '{:,.2f}'.format(stochastic_cost_pessimistic)
print('Pessimistic stochastic cost: ', stochastic_cost_pessimistic_readable)
#log in txt.file
with open('results.txt', 'a') as f:
    f.write('Results with tradeoff solution'+'\n')
    f.write('New cables: '+str(ampl.getVariable('new_cables').getValues().toPandas())+'\n')
    f.write('P_min: '+str(ampl.getParameter('P_min').getValues().toPandas())+'\n')
    f.write('Deterministic cost: '+str(deterministic_cost_readable)+'\n')
    f.write('Stochastic cost: '+str(stochastic_cost_readable)+'\n')
    f.write('Pessimistic stochastic cost: '+str(stochastic_cost_pessimistic_readable)+'\n')
    f.write(''+'\n')


x_pd = ampl.getVariable('x').getValues().toPandas()

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "tradeoff_solution_cable_routing.png")

####################### Results with pessimistic solution
print('')
print('Results with pessimistic solution')
print('')

# #deterministic cost weight of 0.5
ampl.getParameter('deterministic_cost_weight').set(0.5)

# #stochastic cost weight of 0
ampl.getParameter('stochastic_cost_weight').set(0)

# # stochastic cost weight pessimistic of 0.5
ampl.getParameter('stochastic_cost_weight_pessimistic').set(0.5)


ampl.solve()

print('New cables:', ampl.getVariable('new_cables').getValues().toPandas())
print('P_min:', ampl.getParameter('P_min').getValues().toPandas())

deterministic_cost = ampl.getVariable('deterministic_cost').getValues().toPandas().iloc[0][0]
deterministic_cost_readable = '{:,.2f}'.format(deterministic_cost)
print('Deterministic cost: ', deterministic_cost_readable)
stochastic_cost = ampl.getVariable('stochastic_cost').getValues().toPandas().iloc[0][0]
stochastic_cost_readable = '{:,.2f}'.format(stochastic_cost)
print('Stochastic cost: ', stochastic_cost_readable)
stochastic_cost_pessimistic = ampl.getVariable('stochastic_cost_pessimistic').getValues().toPandas().iloc[0][0]
stochastic_cost_pessimistic_readable = '{:,.2f}'.format(stochastic_cost_pessimistic)
print('Pessimistic stochastic cost: ', stochastic_cost_pessimistic_readable)
#log in txt.file
with open('results.txt', 'a') as f:
    f.write('Results with pessimistic solution'+'\n')
    f.write('New cables: '+str(ampl.getVariable('new_cables').getValues().toPandas())+'\n')
    f.write('P_min: '+str(ampl.getParameter('P_min').getValues().toPandas())+'\n')
    f.write('Deterministic cost: '+str(deterministic_cost_readable)+'\n')
    f.write('Stochastic cost: '+str(stochastic_cost_readable)+'\n')
    f.write('Pessimistic stochastic cost: '+str(stochastic_cost_pessimistic_readable)+'\n')
    f.write(''+'\n')

x_pd = ampl.getVariable('x').getValues().toPandas()

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "pessimistic_solution_cable_routing.png")

#close ampl
ampl.close()