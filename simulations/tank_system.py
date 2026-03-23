import numpy as np
import matplotlib.pyplot as plt

# Simple first-order system: dy/dt = (-y + K*u)/tau

K = 1.0
tau = 5.0
dt = 0.1

time = np.arange(0, 50, dt)
u = np.ones_like(time)
y = np.zeros_like(time)

for i in range(1, len(time)):
    dy = (-y[i-1] + K * u[i-1]) / tau
    y[i] = y[i-1] + dy * dt

plt.plot(time, y, label="Output (y)")
plt.plot(time, u, '--', label="Input (u)")
plt.xlabel("Time")
plt.ylabel("Response")
plt.title("Tank System Step Response")
plt.legend()
plt.show()