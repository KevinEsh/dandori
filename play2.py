from numpy.random import normal
from numpy import linspace, exp, maximum
import matplotlib.pyplot as plt

size = 100
x = linspace(1, 5, size)
y = maximum(exp(x) + normal(0, 10, size=size), 0)

plt.plot(x, y, 'o')
plt.savefig("test.jpg")
