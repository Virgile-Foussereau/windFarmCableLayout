param n := 30;

set V;
set T;
set A := {i in V, j in V: i != j};
set W := 1..n;
set VxW := {i in V, w in W};

param x_coord{V};
param y_coord{V};
param type{V};
param P{h in V} >= 0, default 1;
param P_deviation{(h,w) in VxW} >=-1, <=1, default 0;

param P_sum := sum{i in V: type[i]=1} P[i];
param P_min{w in W} := P_sum + sum{i in V: type[i]=1} P_deviation[i,w];

param k{t in T} > 0;
param u{t in T} > 0;
param max_usage{t in T} > 0;

param C > 0;

param c{i in V, j in V, t in T} :=
  u[t] * sqrt( (x_coord[i]-x_coord[j])^2 + (y_coord[i]-y_coord[j])^2 );

var x{(i,j) in A, t in T}, binary;
var y{(i,j) in A}, binary;
var f{(i,j) in A} >= 0;

var x_new{(i,j) in A, t in T, w in W}, binary;
var y_new{(i,j) in A, w in W}, binary;
var f_new{(i,j) in A, w in W} >= 0;

var new_cables{w in W} >= 0, integer;

subject to new_cables_def{w in W}:
	new_cables[w] = sum{(i,j) in A, t in T} x_new[i,j,t,w];

var deterministic_cost >= 0;

subject to deterministic_cost_def:
	deterministic_cost = sum{(i,j) in A, t in T} c[i,j,t]*x[i,j,t];

var stochastic_cost >= 0;

subject to stochastic_cost_def:
	stochastic_cost = (sum{(i,j) in A, t in T, w in W} c[i,j,t]*x_new[i,j,t,w])/n;

var stochastic_cost_pessimistic >= 0;

var y_worst_cost{w in W}, binary;

subject to stochastic_cost_pessimistic_def{w in W}:
	stochastic_cost_pessimistic >= sum{(i,j) in A, t in T} c[i,j,t]*x_new[i,j,t,w];

subject to y_worst_cost_def:
	sum {w in W} y_worst_cost[w] = 1;

subject to stochastic_cost_pessimistic_def2{w in W}:
	stochastic_cost_pessimistic <= (sum{(i,j) in A, t in T} c[i,j,t]*x_new[i,j,t,w]) + 1000000*(1-y_worst_cost[w]);

param deterministic_cost_weight, default 0.5;

param stochastic_cost_weight, default 0.5;

param stochastic_cost_weight_pessimistic, default 0;

minimize of:
	deterministic_cost_weight*deterministic_cost + stochastic_cost_weight*stochastic_cost + stochastic_cost_weight_pessimistic*stochastic_cost_pessimistic;

### Deterministic part
subject to cable_built{(i,j) in A}:
	sum{t in T} x[i,j,t] = y[i,j];
	
subject to power{h in V: type[h]=1}:
	sum{i in V: (i,h) in A} (f[h,i] - f[i,h]) <= P[h];

subject to flow_def{(i,j) in A}:
	f[i,j] <= sum{t in T} k[t]*x[i,j,t];
	
subject to one_cable_out{h in V: type[h]=1}:	
	sum{j in V: (h,j) in A} y[h,j] = 1;

subject to zero_cable_out{h in V: type[h]=-1}:	
	sum{j in V: (h,j) in A} y[h,j] = 0;

subject to capacity{h in V: type[h]=-1}:
	sum{i in V: (i,h) in A} y[i,h] <= C;

subject to power_to_source{w in W, h in V: type[h]=-1}:
	sum{i in V: (i,h) in A} f[i,h] >= sum{i in V: type[i]=1} P[i];


### Stochastic part
subject to cable_built_new{(i,j) in A, w in W}:
	sum{t in T} x_new[i,j,t,w] = y_new[i,j,w];

subject to power_new{w in W, h in V: type[h]=1}:
	sum{i in V: (i,h) in A} (f_new[h,i,w] - f_new[i,h,w]) <= P[h] + P_deviation[h,w];

subject to flow_def_new{(i,j) in A, w in W}:
	f_new[i,j,w] <= sum{t in T} k[t]*(x_new[i,j,t,w]+x[i,j,t]);

subject to zero_cable_out_new{w in W, h in V: type[h]=-1}:
	sum{j in V: (h,j) in A} y_new[h,j,w] = 0;

subject to capacity_new{w in W, h in V: type[h]=-1}:
	sum{i in V: (i,h) in A} (y_new[i,h,w] + y[i,h]) <= C;

subject to power_to_source_new{w in W, h in V: type[h]=-1}:
	sum{i in V: (i,h) in A} f_new[i,h,w] >= P_min[w];