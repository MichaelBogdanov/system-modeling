"""
Лабораторная работа 2
"""

import random


# Для повторяемого результата
random.seed(1337)

# Точные значения для f(x) = 4x^3 на (0, 1)
M_exact = 4 / 5
D_exact = 2 / 75

def generate_sample(N):
    # Метод обратной функции:
    # F(x) = x^4, значит x = r^(1/4)
    return [random.random() ** 0.25 for _ in range(N)]

def calc_estimates(sample):
    N = len(sample)
    m = sum(sample) / N
    g = sum((x - m) ** 2 for x in sample) / (N - 1)
    return m, g

# Два размера выборки
sizes = [100, 500]

# Считаем данные
rows = []
for N in sizes:
    sample = generate_sample(N)
    m, g = calc_estimates(sample)

    rows.append([
        N,
        M_exact,
        m,
        abs(M_exact - m),
        D_exact,
        g,
        abs(D_exact - g),
    ])

# Красивый вывод таблицы
headers = ["N", "Mx", "m", "|Mx - m|", "Dx", "g", "|Dx - g|"]

# Ширины столбцов
widths = [8, 12, 12, 12, 12, 12, 12]

def fmt(value, col_index):
    if col_index == 0:
        return f"{value:d}"
    return f"{value:.6f}"

# Заголовок
line = ""
for h, w in zip(headers, widths):
    line += f"{h:^{w}}"
print(line)
print("-" * len(line))

# Строки таблицы
for row in rows:
    out = ""
    for i, val in enumerate(row):
        out += f"{fmt(val, i):^{widths[i]}}"
    print(out)
