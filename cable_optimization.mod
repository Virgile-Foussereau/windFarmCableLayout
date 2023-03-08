set V;
set T;
set A := {i in V, j in V: i != j};

param x_coord{V};
param y_coord{V};
param type{V};
param P{h in V} >= 0, default 1;

param k{t in T} > 0;
param u{t in T} > 0;
param max_usage{t in T} > 0;

param C > 0;

param c{i in V, j in V, t in T} :=
  u[t] * sqrt( (x_coord[i]-x_coord[j])^2 + (y_coord[i]-y_coord[j])^2 );

var x{(i,j) in A, t in T}, binary;
var y{(i,j) in A}, binary;
var f{(i,j) in A} >= 0;

minimize of:
	sum{(i,j) in A, t in T} c[i,j,t]*x[i,j,t];
	
subject to cable_built{(i,j) in A}:
	sum{t in T} x[i,j,t] = y[i,j];
	
subject to power{h in V: type[h]=1}:
	sum{i in V: (i,h) in A} (f[h,i] - f[i,h]) = P[h];

subject to flow_def{(i,j) in A}:
	f[i,j] <= sum{t in T} k[t]*x[i,j,t];
	
subject to one_cable_out{h in V: type[h]=1}:	
	sum{j in V: (h,j) in A} y[h,j] = 1;

subject to zero_cable_out{h in V: type[h]=-1}:	
	sum{j in V: (h,j) in A} y[h,j] = 0;

subject to capacity{h in V: type[h]=-1}:
	sum{i in V: (i,h) in A} y[i,h] <= C;