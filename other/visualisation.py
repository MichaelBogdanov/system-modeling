"""
Визуализатор распределений случайных величин с помощью Tkinter и Matplotlib

Реализовано для трех типов распределений:
- Равномерное распределение (Uniform)
- Показательное распределение (Exponential)
- Нормальное распределение (Normal)

Пользовательский интерфейс позволяет выбирать тип распределения, задавать его параметры, размер выборки, число корзин для гистограммы и опционально фиксировать seed для генератора случайных чисел. Графики плотности распределения и функции распределения строятся на основе теоретических формул и эмпирической выборки (если она отображается). Внизу отображается статистика по выборке
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable, Optional

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# -----------------------------
# Спецификации распределений
# -----------------------------


@dataclass(frozen=True)
class DistributionSpec:
    key: str
    title: str
    parameter_names: tuple[str, ...]


DISTRIBUTIONS = {
    "uniform": DistributionSpec("uniform", "Равномерное распределение", ("a", "b")),
    "exponential": DistributionSpec("exponential", "Показательное распределение", ("lambda",)),
    "normal": DistributionSpec("normal", "Нормальное распределение", ("mu", "sigma")),
}


# -----------------------------
# Математические функции распределений
# -----------------------------


def uniform_pdf(x: np.ndarray, a: float, b: float) -> np.ndarray:
    y = np.zeros_like(x, dtype=float)
    mask = (x >= a) & (x <= b)
    y[mask] = 1.0 / (b - a)
    return y


def uniform_cdf(x: np.ndarray, a: float, b: float) -> np.ndarray:
    y = np.zeros_like(x, dtype=float)
    y[x > b] = 1.0
    middle = (x >= a) & (x <= b)
    y[middle] = (x[middle] - a) / (b - a)
    return y


def exponential_pdf(x: np.ndarray, lam: float) -> np.ndarray:
    y = np.zeros_like(x, dtype=float)
    mask = x >= 0
    y[mask] = lam * np.exp(-lam * x[mask])
    return y


def exponential_cdf(x: np.ndarray, lam: float) -> np.ndarray:
    y = np.zeros_like(x, dtype=float)
    mask = x >= 0
    y[mask] = 1.0 - np.exp(-lam * x[mask])
    return y


def normal_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    z = (x - mu) / sigma
    return np.exp(-0.5 * z * z) / (sigma * math.sqrt(2.0 * math.pi))


def normal_cdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    z = (x - mu) / (sigma * math.sqrt(2.0))
    return 0.5 * (1.0 + np.vectorize(math.erf)(z))


# -----------------------------
# Приложение для визуализации распределений
# -----------------------------


class DistributionVisualizerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Визуализатор распределений случайных величин")
        self.geometry("1280x820")
        self.minsize(1120, 760)

        self._rng = np.random.default_rng()
        self._parameter_vars: dict[str, tk.StringVar] = {}

        self.distribution_var = tk.StringVar(value="uniform")
        self.view_var = tk.StringVar(value="both")
        self.sample_size_var = tk.StringVar(value="5000")
        self.bins_var = tk.StringVar(value="40")
        self.seed_var = tk.StringVar(value="")
        self.show_samples_var = tk.BooleanVar(value=True)

        self._build_style()
        self._build_ui()
        self._sync_parameter_form()
        self.after(100, self.redraw)

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", padding=6)
        style.configure("TLabel", padding=2)
        style.configure("TButton", padding=(10, 6))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(root, width=360)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left.pack_propagate(False)

        right = ttk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        title = ttk.Label(left, text="Параметры", style="Header.TLabel")
        title.pack(anchor=tk.W, pady=(0, 8))

        dist_box = ttk.LabelFrame(left, text="Тип распределения")
        dist_box.pack(fill=tk.X, pady=(0, 10))
        for key, spec in DISTRIBUTIONS.items():
            ttk.Radiobutton(
                dist_box,
                text=spec.title,
                value=key,
                variable=self.distribution_var,
                command=self._on_distribution_changed,
            ).pack(anchor=tk.W, padx=6, pady=2)

        self.param_box = ttk.LabelFrame(left, text="Параметры распределения")
        self.param_box.pack(fill=tk.X, pady=(0, 10))

        view_box = ttk.LabelFrame(left, text="Вид графика")
        view_box.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(view_box, text="Плотность и выборка", value="both", variable=self.view_var).pack(
            anchor=tk.W, padx=6, pady=2
        )
        ttk.Radiobutton(view_box, text="Только плотность / функция", value="theory", variable=self.view_var).pack(
            anchor=tk.W, padx=6, pady=2
        )

        general_box = ttk.LabelFrame(left, text="Общие настройки")
        general_box.pack(fill=tk.X, pady=(0, 10))
        self._add_labeled_entry(general_box, "Размер выборки", self.sample_size_var, row=0)
        self._add_labeled_entry(general_box, "Число корзин", self.bins_var, row=1)
        self._add_labeled_entry(general_box, "Seed (необязательно)", self.seed_var, row=2)
        ttk.Checkbutton(general_box, text="Показывать выборку", variable=self.show_samples_var).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2)
        )
        general_box.columnconfigure(1, weight=1)

        buttons = ttk.Frame(left)
        buttons.pack(fill=tk.X, pady=(4, 10))
        ttk.Button(buttons, text="Построить график", command=self.redraw).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(buttons, text="Сброс", command=self.reset_defaults).pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="Готово к построению графика.")
        status = ttk.Label(left, textvariable=self.status_var, wraplength=330, justify=tk.LEFT)
        status.pack(fill=tk.X, pady=(6, 0))

        self.figure = Figure(figsize=(8.8, 7.0), dpi=100, tight_layout=True)
        self.ax_top = self.figure.add_subplot(2, 1, 1)
        self.ax_bottom = self.figure.add_subplot(2, 1, 2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._parameter_widgets: dict[str, tuple[ttk.Entry, ttk.Label]] = {}

    def _add_labeled_entry(self, parent: ttk.Widget, label: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", padx=6, pady=4)

    def _on_distribution_changed(self) -> None:
        self._sync_parameter_form()
        self.redraw()

    def _sync_parameter_form(self) -> None:
        for child in self.param_box.winfo_children():
            child.destroy()
        self._parameter_vars.clear()
        self._parameter_widgets.clear()

        dist = self.distribution_var.get()
        spec = DISTRIBUTIONS[dist]

        if dist == "uniform":
            defaults = {"a": "0", "b": "1"}
            descriptions = {"a": "Нижняя граница", "b": "Верхняя граница"}
        elif dist == "exponential":
            defaults = {"lambda": "1"}
            descriptions = {"lambda": "Интенсивность λ"}
        else:
            defaults = {"mu": "0", "sigma": "1"}
            descriptions = {"mu": "Матожидание μ", "sigma": "Стандартное отклонение σ"}

        for row, name in enumerate(spec.parameter_names):
            ttk.Label(self.param_box, text=descriptions[name]).grid(row=row, column=0, sticky="w", padx=6, pady=4)
            var = tk.StringVar(value=defaults[name])
            self._parameter_vars[name] = var
            entry = ttk.Entry(self.param_box, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", padx=6, pady=4)
            self._parameter_widgets[name] = (entry, ttk.Label(self.param_box))

        self.param_box.columnconfigure(1, weight=1)

    def reset_defaults(self) -> None:
        self.distribution_var.set("uniform")
        self.view_var.set("both")
        self.sample_size_var.set("5000")
        self.bins_var.set("40")
        self.seed_var.set("")
        self.show_samples_var.set(True)
        self._sync_parameter_form()
        self.redraw()

    def _parse_int(self, value: str, field_name: str, min_value: int = 1, max_value: Optional[int] = None) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"Поле «{field_name}» должно быть целым числом.") from exc
        if parsed < min_value:
            raise ValueError(f"Поле «{field_name}» должно быть не меньше {min_value}.")
        if max_value is not None and parsed > max_value:
            raise ValueError(f"Поле «{field_name}» должно быть не больше {max_value}.")
        return parsed

    def _parse_float(self, value: str, field_name: str) -> float:
        try:
            return float(value.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"Поле «{field_name}» должно быть числом.") from exc

    def _read_parameters(self) -> dict[str, float]:
        dist = self.distribution_var.get()
        params: dict[str, float] = {}
        for name, var in self._parameter_vars.items():
            params[name] = self._parse_float(var.get().strip(), name)

        if dist == "uniform":
            a = params["a"]
            b = params["b"]
            if not a < b:
                raise ValueError("Для равномерного распределения нужно, чтобы a < b.")
        elif dist == "exponential":
            lam = params["lambda"]
            if lam <= 0:
                raise ValueError("Для показательного распределения λ должно быть больше 0.")
        elif dist == "normal":
            sigma = params["sigma"]
            if sigma <= 0:
                raise ValueError("Для нормального распределения σ должно быть больше 0.")
        return params

    def _make_rng(self) -> np.random.Generator:
        seed_text = self.seed_var.get().strip()
        if not seed_text:
            return np.random.default_rng()
        seed = self._parse_int(seed_text, "Seed", min_value=0, max_value=2**32 - 1)
        return np.random.default_rng(seed)

    def _sample_distribution(self, rng: np.random.Generator, size: int, params: dict[str, float]) -> np.ndarray:
        dist = self.distribution_var.get()
        if dist == "uniform":
            return rng.uniform(params["a"], params["b"], size=size)
        if dist == "exponential":
            scale = 1.0 / params["lambda"]
            return rng.exponential(scale=scale, size=size)
        return rng.normal(loc=params["mu"], scale=params["sigma"], size=size)

    def _get_theory_functions(self, params: dict[str, float]) -> tuple[Callable[[np.ndarray], np.ndarray], Callable[[np.ndarray], np.ndarray]]:
        dist = self.distribution_var.get()
        if dist == "uniform":
            return (
                lambda x: uniform_pdf(x, params["a"], params["b"]),
                lambda x: uniform_cdf(x, params["a"], params["b"]),
            )
        if dist == "exponential":
            return (
                lambda x: exponential_pdf(x, params["lambda"]),
                lambda x: exponential_cdf(x, params["lambda"]),
            )
        return (
            lambda x: normal_pdf(x, params["mu"], params["sigma"]),
            lambda x: normal_cdf(x, params["mu"], params["sigma"]),
        )

    def _make_x_grid(self, params: dict[str, float], sample: Optional[np.ndarray]) -> np.ndarray:
        dist = self.distribution_var.get()
        if dist == "uniform":
            a, b = params["a"], params["b"]
            padding = max(0.05 * (b - a), 0.5)
            return np.linspace(a - padding, b + padding, 800)
        if dist == "exponential":
            lam = params["lambda"]
            right = max(8.0 / lam, 5.0)
            if sample is not None and sample.size:
                right = max(right, float(np.quantile(sample, 0.995)) * 1.1)
            return np.linspace(0.0, right, 800)
        mu, sigma = params["mu"], params["sigma"]
        left = mu - 4.5 * sigma
        right = mu + 4.5 * sigma
        if sample is not None and sample.size:
            left = min(left, float(np.quantile(sample, 0.005)) - 0.5 * sigma)
            right = max(right, float(np.quantile(sample, 0.995)) + 0.5 * sigma)
        return np.linspace(left, right, 800)

    def redraw(self) -> None:
        try:
            sample_size = self._parse_int(self.sample_size_var.get().strip(), "Размер выборки", min_value=1, max_value=5_000_000)
            bins = self._parse_int(self.bins_var.get().strip(), "Число корзин", min_value=5, max_value=500)
            params = self._read_parameters()
            rng = self._make_rng()
            sample = self._sample_distribution(rng, sample_size, params) if self.show_samples_var.get() else None
            pdf_func, cdf_func = self._get_theory_functions(params)
            x = self._make_x_grid(params, sample)

            self._draw_plots(x, pdf_func, cdf_func, sample, bins)
            self._update_status(sample, params)
            self.canvas.draw_idle()
        except Exception as exc:
            messagebox.showerror("Ошибка ввода", str(exc))

    def _draw_plots(
        self,
        x: np.ndarray,
        pdf_func: Callable[[np.ndarray], np.ndarray],
        cdf_func: Callable[[np.ndarray], np.ndarray],
        sample: Optional[np.ndarray],
        bins: int,
    ) -> None:
        self.figure.clf()

        if self.view_var.get() == "theory":
            ax1 = self.figure.add_subplot(1, 1, 1)
            self._draw_pdf(ax1, x, pdf_func, sample, bins)
        else:
            ax1 = self.figure.add_subplot(2, 1, 1)
            ax2 = self.figure.add_subplot(2, 1, 2)
            self._draw_pdf(ax1, x, pdf_func, sample, bins)
            self._draw_cdf(ax2, x, cdf_func, sample)

        self.figure.tight_layout()

    def _draw_pdf(
        self,
        ax,
        x: np.ndarray,
        pdf_func: Callable[[np.ndarray], np.ndarray],
        sample: Optional[np.ndarray],
        bins: int,
    ) -> None:
        y = pdf_func(x)
        ax.plot(x, y, linewidth=2.2, label="Теоретическая плотность")
        if sample is not None and sample.size:
            ax.hist(sample, bins=bins, density=True, alpha=0.35, label="Гистограмма выборки")
        ax.set_title(self._current_title("Плотность распределения"))
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")

    def _draw_cdf(
        self,
        ax,
        x: np.ndarray,
        cdf_func: Callable[[np.ndarray], np.ndarray],
        sample: Optional[np.ndarray],
    ) -> None:
        y = cdf_func(x)
        ax.plot(x, y, linewidth=2.2, label="Теоретическая функция распределения")
        if sample is not None and sample.size:
            sorted_sample = np.sort(sample)
            ecdf = np.arange(1, sorted_sample.size + 1) / sorted_sample.size
            ax.step(sorted_sample, ecdf, where="post", alpha=0.7, label="Эмпирическая функция распределения")
        ax.set_title("Функция распределения")
        ax.set_xlabel("x")
        ax.set_ylabel("F(x)")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")

    def _current_title(self, suffix: str) -> str:
        return f"{DISTRIBUTIONS[self.distribution_var.get()].title} — {suffix}"

    def _update_status(self, sample: Optional[np.ndarray], params: dict[str, float]) -> None:
        if sample is None or not sample.size:
            self.status_var.set("Построен теоретический график без выборки.")
            return

        mean = float(np.mean(sample))
        std = float(np.std(sample, ddof=1)) if sample.size > 1 else 0.0
        mn = float(np.min(sample))
        mx = float(np.max(sample))
        self.status_var.set(
            f"Выборка: n={sample.size}. Среднее={mean:.4f}, std={std:.4f}, min={mn:.4f}, max={mx:.4f}."
        )


if __name__ == "__main__":
    app = DistributionVisualizerApp()
    app.mainloop()
