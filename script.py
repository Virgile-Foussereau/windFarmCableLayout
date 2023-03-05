from amplpy import AMPL, Environment
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from ast import literal_eval as make_tuple
import os

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
    #plt.show()
    plt.savefig(name)

def plot_multiple_cable_layouts(x_pd, pos, deterministic_cost=None, perturbation=False, x_pd2=None, P_deviation_pd=None):
    size = (1+np.sqrt(1+4*len(x_pd)))/2
    size = int(size)
    print("size of matrix: ", size)
    G2 = nx.Graph()
    for i in range(len(x_pd)):
        if int(x_pd.iloc[i][0])==1:
            idx_1 = int(x_pd.index[i][0]) - 1
            idx_2 = int(x_pd.index[i][1]) - 1
            cableType = int(x_pd.index[i][2])
            G2.add_edge(idx_1, idx_2, color='C'+str(cableType-1))


    #figure with legend
    fig = plt.figure()
    k = 1+len(x_pd2)//len(x_pd)
    # k graphs to plot
    nrow = int(np.ceil(np.sqrt(k)))
    ncol = int(np.ceil(k/nrow))
    ax = fig.add_subplot(nrow, ncol, 1)
    for cableType in range(1,4):
        ax.scatter([], [], c='C'+str(cableType-1), label='cable type '+str(cableType))


    #plot matrix as a graph with color
    nx.draw_networkx(G2, pos=pos, node_size=60,  with_labels=False, edge_color=[G2[u][v]['color'] for u,v in G2.edges()], ax=ax)

    #add title
    if deterministic_cost is not None:
        plt.title('Cable layout with deterministic cost: '+str(deterministic_cost))

    plt.legend()

    #add new subplot for each scenario
    for i in range(len(x_pd2)//len(x_pd)):
        ax = fig.add_subplot(nrow, ncol, i+2)
        G_new = G2.copy()
        new_cables_count = 0
        for j in range(len(x_pd)):
            if int(x_pd2.iloc[i*len(x_pd)+j][0])==1:
                new_cables_count += 1
                idx_1 = int(x_pd2.index[i*len(x_pd)+j][0]) - 1
                idx_2 = int(x_pd2.index[i*len(x_pd)+j][1]) - 1
                cableType = int(x_pd2.index[i*len(x_pd)+j][2])
                G_new.add_edge(idx_1, idx_2, color='r')

        nx.draw_networkx(G_new, pos=pos, node_size=60, with_labels=False, edge_color=[G_new[u][v]['color'] for u,v in G_new.edges()], ax=ax)
        plt.title('Scenario '+str(i+1)+' with '+str(new_cables_count)+' new cables')
        for cableType in range(1,4):
            ax.scatter([], [], c='C'+str(cableType-1), label='cable type '+str(cableType))
        ax.scatter([], [], c='r', label='new cable')
        plt.legend()
        plt.tight_layout()
    
    plt.show()

ampl = AMPL(Environment(r'/Users/virgilefoussereau/Documents/ampl_macos64'))
ampl.reset()

ampl.read('cable_optimization_stochastic.mod')
ampl.readData('wf02_cb01_capex.dat')

#get set VxW
VxW_pd = ampl.getSet('VxW').getValues().toPandas()

#normal distribution for each node in V and each scenario in W truncated between -0.5 and 0.5
P_deviation_pd = pd.DataFrame(np.random.normal(0, 0.5, len(VxW_pd)), index=VxW_pd.index)
P_deviation_pd = P_deviation_pd.clip(lower=-0.5, upper=0.5)

ampl.getParameter('P_deviation').setValues(P_deviation_pd)

# ampl.getObjective('of_pessimistic').drop()

ampl.setOption('solver', 'cplex')
ampl.setOption('cplex_options', 'timelimit=3600 iisfind 1')

####################### Results with deterministic solution
print('')
print('Results with deterministic solution')
print('')

#load deterministic solution from csv
if os.path.isfile('deterministic_solution.csv'):
    x_pd = ampl.getVariable('x').getValues().toPandas()
    index_x_pd = x_pd.index
    index_x_pd = x_pd.index
    x_pd = pd.read_csv('deterministic_solution.csv', index_col=0)
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

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "deterministic_solution_30_scenarios.png")

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

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "tradeoff_solution_30_scenarios.png")

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

plot_cable_layout(x_pd, pos, deterministic_cost_readable, "pessimistic_solution_30_scenarios.png")

#close ampl
ampl.close()