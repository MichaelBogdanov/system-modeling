"""
Лабораторная работа 1
Таблица результатов для N = 100 и N = 500
"""

import random
import pandas as pd


# ДАННЫЕ ВАРИАНТА
x_values = [4, -7, 6]
p = [0.4, 0.1, 0.5]

# Сколько первых значений показать
q = 14

# Для одинакового результата при каждом запуске
random.seed(32)

# ПРОВЕРКА ВЕРОЯТНОСТЕЙ
if abs(sum(p) - 1) > 1e-12:
    raise ValueError("Сумма вероятностей должна равняться 1")

# КУМУЛЯТИВНЫЕ ВЕРОЯТНОСТИ
cum_p = []
running_sum = 0
for probability in p:
    running_sum += probability
    cum_p.append(running_sum)

# ФУНКЦИЯ МОДЕЛИРОВАНИЯ
def generate_sample(N):
    simulated = []
    for _ in range(N):
        r = random.random()  # число от 0 до 1
        for i, cp in enumerate(cum_p):
            if r < cp:
                simulated.append(x_values[i])
                break
    return simulated

# ТОЧНЫЕ ЗНАЧЕНИЯ
M_exact = sum(x_values[k] * p[k] for k in range(len(x_values)))
D_exact = sum(p[k] * (x_values[k] - M_exact) ** 2 for k in range(len(x_values)))

# ФУНКЦИЯ ДЛЯ РАСЧЁТА ОЦЕНОК
def calculate_row(N):
    sample = generate_sample(N)

    # Первые q значений — просто для контроля
    print(f"\nПервые {q} значений при N = {N}:")
    print(", ".join(map(str, sample[:q])))

    # Оценка матожидания
    m = sum(sample) / N

    # Несмещённая оценка дисперсии
    g = sum(x ** 2 for x in sample) / (N - 1) - (N / (N - 1)) * m ** 2

    return {
        "N": N,
        "Mx": M_exact,
        "m": m,
        "|Mx - m|": abs(M_exact - m),
        "Dx": D_exact,
        "g": g,
        "|Dx - g|": abs(D_exact - g),
    }

# РАСЧЁТ ДЛЯ ДВУХ ЗНАЧЕНИЙ N
results = [
    calculate_row(100),
    calculate_row(500)
]

# ВЫВОД ТАБЛИЦЫ
df = pd.DataFrame(results)

# Округлим для красивого вывода
df = df.round(6)

print("\nИтоговая таблица:")
print(df.to_string(index=False, justify="justify", col_space=8))
