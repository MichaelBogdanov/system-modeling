import matplotlib.pyplot as plt

values = [-7, 4, 6]
x_vals = [0.1, 0.4, 0.5]
F_vals = [x_vals[0]] + [sum(x_vals[:i + 1]) for i in range(1, len(x_vals))]

fig, ax = plt.subplots(figsize=(8, 5))

x_min, x_max = min(values) - 1, max(values) + 1

for i in range(len(values)):
    ax.plot(values[i], F_vals[i], 'ko', markersize=5) 

for i in range(len(values) - 1):
    ax.annotate('', xy=(values[i], F_vals[i]), xytext=(values[i + 1], F_vals[i]), arrowprops=dict(arrowstyle='->', lw=1.5))

ax.set_xlim(x_min, x_max)
ax.set_ylim(-0.1, 1.1)

ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

ax.set_xticks(values, [str(v) for v in values])
ax.set_yticks(F_vals)
ax.tick_params(axis='both', which='major', labelsize=10)

ax.vlines(values, 0, F_vals, colors='gray', linestyles='dashed', lw=1)
ax.hlines(F_vals, 0, values, colors='gray', linestyles='dashed', lw=1)

ax.set_xlabel('x', loc='right', fontsize=12, fontstyle='italic')
ax.set_ylabel('F(x)', loc='top', rotation=0, fontsize=12, fontstyle='italic')

plt.title('Функция распределения F(x)', fontsize=14, pad=20)

plt.show()
