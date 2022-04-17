import numpy as np
import matplotlib.pyplot as plt

times = np.array([
    0.04,
    0.05,
    0.12,
    0.20,
    0.36,
    0.44,
    0.42,
    0.57,
    0.68,
    0.44,
    1.05,
    2.24,
    4.07,
    6.38,
    9.55,
    13.61,
    17.85,
    22.74,
    28.44,
    35.06,
    42.72,
    51.43,
    61.34,
    69.01,
    80.99,
    94.44,
    104.46,
    121.95,
    134.30,
    145.41,
    157.64,
    174.12,
    190.82,
    212.59,
    239.39,
    272.77,
    313.07,
    361.81,
    420.87,
    480.68,
    558.27,
    636.77,
])

nums = np.arange(5, 5*times.shape[0] + 5, 5)

plt.title("Gráfica comparativa de ejecución de FlowShop")
plt.ylabel("Log Tiempo de cómputo en [$min$]")
plt.xlabel("Número de ordenes")
plt.grid(True)
plt.plot(nums, times/60, 'k^')
plt.savefig("test.jpg")
