"""
Лабораторная работа 1
"""
# Ввод данных
x_values = [4, -7, 6]
p = [0.4, 0.1, 0.5]
N = 1_000_000
q = 14

# Проверка: сумма вероятностей равна 1
if sum(p) != 1:
    raise ValueError("Сумма вероятностей должна равняться 1")

# Кумулятивная сумма вероятностей
cum_p = []
running_sum = 0
for probability in p:
    running_sum += probability
    cum_p.append(running_sum)

# Моделирование распределения
import random

simulated = []
for _ in range(N):
    r = random.random()  # Случайное число от 0 до 1
    for i, cp in enumerate(cum_p):
        if r < cp:
            simulated.append(x_values[i])  # Добавляем соответствующее значение x в список моделирования
            break

# Вывод первых q результатов:
print(f"Первые {q} сгенерированных значений: {', '.join(map(str, simulated[:q]))}")

# Теоретическое матожидание и дисперсия (по формулам)
M = sum(x_values[k] * p[k] for k in range(len(x_values)))
D = sum(p[k] * (x_values[k] - M) ** 2 for k in range(len(x_values)))
print(f"Теоретическое матожидание: {M}")
print(f"Теоретическая дисперсия: {D}")

# Выборочные оценки
m = sum(simulated) / N
g = sum(x ** 2 for x in simulated) / (N - 1) - N / (N - 1) * m ** 2  # Выборочная дисперсия с поправкой на смещение
print(f"Выборочное матожидание: {m}")
print(f"Выборочная дисперсия: {g}")
