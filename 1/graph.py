import matplotlib.pyplot as plt


x_vals = [-7, 4, 6]
p_vals = [0.1, 0.4, 0.5]
F_vals = [0, 0.1, 0.5, 1.0]

fig, ax = plt.subplots(figsize=(8, 5))

x_min, x_max = -10, 9

ax.annotate('', xy=(x_min, 0), xytext=(-7, 0), arrowprops=dict(arrowstyle='<-', lw=1.5))
ax.plot(-7, 0, 'ko', markersize=5) 

ax.annotate('', xy=(-7, 0.1), xytext=(4, 0.1), arrowprops=dict(arrowstyle='->', lw=1.5))
ax.plot(4, 0.1, 'ko', markersize=5)

ax.annotate('', xy=(4, 0.5), xytext=(6, 0.5), arrowprops=dict(arrowstyle='->', lw=1.5))
ax.plot(6, 0.5, 'ko', markersize=5)

ax.annotate('', xy=(6, 1.0), xytext=(x_max, 1.0), arrowprops=dict(arrowstyle='->', lw=1.5))

ax.set_xlim(x_min, x_max)
ax.set_ylim(-0.1, 1.2)

ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

ax.set_xticks(x_vals)
ax.set_yticks([0.1, 0.5, 1.0])
ax.tick_params(axis='both', which='major', labelsize=10)

ax.vlines(x_vals[1:], 0, F_vals[1:3], colors='gray', linestyles='dashed', lw=1)
ax.hlines(F_vals[1:], 0, x_vals, colors='gray', linestyles='dashed', lw=1)

ax.set_xlabel('x', loc='right', fontsize=12, fontstyle='italic')
ax.set_ylabel('F(x)', loc='top', rotation=0, fontsize=12, fontstyle='italic')

plt.title('Функция распределения F(x)', fontsize=14, pad=20)

plt.show()
