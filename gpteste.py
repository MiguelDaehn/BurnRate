import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

df = pd.DataFrame({
            'x': [ 1000, 3250, 5500, 10000, 32500, 55000, 77500, 100000, 200000 ],
            'y': [ 1100, 500, 288, 200, 113, 67, 52, 44, 5 ]
        })
df.plot(x='x', y='y', kind='line', style='--ro', figsize=(10, 5))


x = np.asarray([ 1000, 3250, 5500, 10000, 32500, 55000, 77500, 100000, 200000 ])
y = np.asarray([ 1100, 500, 288, 200, 113, 67, 52, 44, 5 ])

def func_powerlaw(x, m, c, c0):
    return c0 + x**m * c

target_func = func_powerlaw

pars,sol0 = curve_fit(func_powerlaw, x, y, p0 = np.asarray([-1,10**5,0]))
c0,c,m = pars
# Extract the parameters

# Print the parameters
print(f"Estimated parameters:")
print(f"c0: {c0}")
print(f"c: {c}")
print(f"m: {m}")

plt.figure(figsize=(10, 5))
plt.plot(x, target_func(x, *pars), '--')
plt.plot(x, y, 'ro')
plt.legend()
plt.show()