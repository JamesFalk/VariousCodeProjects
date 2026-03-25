import numpy as np
import matplotlib.pyplot as plt

# Parameters
r1, r2, r3 = 3.8, 3.85, 3.9  # Chaos parameters for three altcoins
x1, x2, x3 = 0.005404, 0.01, 0.015  # Normalized initial prices (Popcat-like, Solana-like, new token)
n = 100  # Days

# Simulate
x1_vals = [x1]
x2_vals = [x2]
x3_vals = [x3]
for i in range(n-1):
    x1_vals.append(r1 * x1_vals[-1] * (1 - x1_vals[-1]))
    x2_vals.append(r2 * x2_vals[-1] * (1 - x2_vals[-1]))
    x3_vals.append(r3 * x3_vals[-1] * (1 - x3_vals[-1]))

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x1_vals, label='Altcoin 1 (Popcat-like)')
plt.plot(x2_vals, label='Altcoin 2 (Solana-like)')
plt.plot(x3_vals, label='Altcoin 3 (New Token)')
plt.title('Chaotic Altcoin Price Trajectories')
plt.xlabel('Days')
plt.ylabel('Normalized Price')
plt.legend()
plt.grid(True)
plt.show()