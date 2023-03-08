from amplpy import AMPL, Environment
import pandas as pd
import sys

#check for arguments
if len(sys.argv) < 2:
    print("Usage: python script_deterministic.py 'path_to_ampl'")
    sys.exit(1)
else:
    path_to_ampl = sys.argv[1]

data_name = 'wf02_cb01_capex'

#transform path_to_ampl as raw string
path_to_ampl = r'{}'.format(path_to_ampl)
ampl = AMPL(Environment(path_to_ampl))
ampl.reset()

ampl.read('cable_optimization.mod')
ampl.readData(data_name+'.dat')

# ampl.setOption('solver', 'cplex')
# ampl.setOption('cplex_options', 'timelimit=30 iisfind 1')

# use matheuristic
ampl.read('cable_optimization_matheuristic.run')

x_pd = ampl.getVariable('x').getValues().toPandas()

#save deterministic solution
x_pd.to_csv('deterministic_solution_'+data_name+'.csv')

print('')
print('Deterministic solution saved to file deterministic_solution_'+data_name+'.csv')