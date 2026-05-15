"""
Нормальное распределение.
Таблица: N, M, m, |M - m|, D, g, |D - g|
"""

import random

# -----------------------------
# ПАРАМЕТРЫ НОРМАЛЬНОГО РАСПРЕДЕЛЕНИЯ
# -----------------------------
mu = 175       # математическое ожидание
sigma = 7    # среднеквадратичное отклонение

# Для повторяемости результата
random.seed(42)

# -----------------------------
# ТОЧНЫЕ ЗНАЧЕНИЯ
# -----------------------------
M_exact = mu
D_exact = sigma ** 2

# -----------------------------
# ФУНКЦИЯ ГЕНЕРАЦИИ ВЫБОРКИ
# -----------------------------
def generate_sample(N):
    return [random.gauss(mu, sigma) for _ in range(N)]

# -----------------------------
# ФУНКЦИЯ ВЫЧИСЛЕНИЯ ОЦЕНОК
# -----------------------------
def calculate_row(N):
    sample = generate_sample(N)

    # Оценка математического ожидания
    m = sum(sample) / N

    # Несмещённая оценка дисперсии
    g = sum((x - m) ** 2 for x in sample) / (N - 1)

    return {
        "N": N,
        "M": M_exact,
        "m": m,
        "|M - m|": abs(M_exact - m),
        "D": D_exact,
        "g": g,
        "|D - g|": abs(D_exact - g),
    }

# -----------------------------
# РАСЧЁТ ДЛЯ ДВУХ ЗНАЧЕНИЙ N
# -----------------------------
rows = [
    calculate_row(100),
    calculate_row(500)
]

# -----------------------------
# КРАСИВЫЙ ВЫВОД ТАБЛИЦЫ
# -----------------------------
headers = ["N", "M", "m", "|M - m|", "D", "g", "|D - g|"]

formatted_rows = []
for row in rows:
    formatted_rows.append([
        f"{row['N']}",
        f"{row['M']:.6f}",
        f"{row['m']:.6f}",
        f"{row['|M - m|']:.6f}",
        f"{row['D']:.6f}",
        f"{row['g']:.6f}",
        f"{row['|D - g|']:.6f}",
    ])

# вычисляем ширину каждого столбца
widths = []
for i, h in enumerate(headers):
    max_len = len(h)
    for row in formatted_rows:
        max_len = max(max_len, len(row[i]))
    widths.append(max_len)

def make_border(left, mid, right):
    parts = ["─" * (w + 2) for w in widths]
    return left + mid.join(parts) + right

def make_row(values):
    cells = [f" {val:^{widths[i]}} " for i, val in enumerate(values)]
    return "│" + "│".join(cells) + "│"

print(make_border("┌", "┬", "┐"))
print(make_row(headers))
print(make_border("├", "┼", "┤"))

for row in formatted_rows:
    print(make_row(row))

print(make_border("└", "┴", "┘"))