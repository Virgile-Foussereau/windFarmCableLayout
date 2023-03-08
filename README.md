# Stochastic optimization for Wind Farm Cable Routing

![alt text](https://windeurope.org/wp-content/uploads/offshore-wind-farm-aerial-high-angle.jpg)

## About

In this project, we introduce uncertainty in the power production for the Wind Farm Cable Routing problem. 
Please find details about this project in the [report](Report_INF569.pdf).

## Requirements

Please install `AMPL`, `Python3` and the following modules :

- `amplpy`
- `numpy`
- `matplotlib`
- `networkx`

## How to run

First find the path to you AMPL installation.

To run the classic deterministic optimization (no uncertainty):

```bash
python3 script_deterministic.py 'paht_to_your_ampl_installation'
```

To run the our pipeline (with uncertainty):

```bash
python3 script.py 'paht_to_your_ampl_installation'
```

## Personalization 

### Number of scenarios
You can change the number of scenarios to consider for stochastic optimization in the file `cable_optimization_stochastic.mod` by changing the value of `n`. More scenarios is more accurate but also more computationally expensive.

### Data change
The data used data is from the wind farm Kentish Flats, located close to Kent in South East England. If you were to change the data, put the name of you `.dat` file in both `script_deterministic.py` and `script.py`, run first `script_deterministic.py` and then run `script.py`. 
