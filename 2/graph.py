import numpy as np
import matplotlib.pyplot as plt

# Интервал плотности
x = np.linspace(0, 1, 90)
y = 4 * x**3

plt.plot(x, y, label='f(x) = 4x^3')

# Нулевая линия вне интервала
plt.axhline(0, color='black', linewidth=0.8)

plt.xlabel('x')
plt.ylabel('f(x)')
plt.title('Плотность распределения f(x) = 4x^3 на (0, 1)')
plt.grid(True)
plt.legend()
plt.show()
