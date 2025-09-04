import tkinter as tk
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


class Range():
	"""
	Хранит диапазон для UI.

	Attributes:
		begin (tk.DoubleVar): Начало
		end (tk.DoubleVar): Конец
		step (tk.DoubleVar): Шаг
	"""

	def __init__(self, settings: list):
		"""
		Извлечение значений диапазона из списка.

		Attributes:
			settings (list): Список значений диапазона
		"""
		self.begin = tk.DoubleVar(value = settings[0])
		self.end = tk.DoubleVar(value = settings[1])
		self.step = tk.DoubleVar(value = settings[2])


class Formula():
	"""
	Хранит параметры формулы для UI.

	Attributes:
		r, b (Range): Коэффициенты функций
		x0 (tk.DoubleVar): Начальное значение x[n]
		n_iter (tk.IntVar): Количество итераций для установления устойчивого режима
		n_draw (tk.IntVar): Количество итераций для отрисовки графика
	"""
	def __init__(self, settings: dict):
		"""
		Извлечение параметров из словаря настроек.

		Attributes:
			settings (dict): Словарь настроек
		"""
		self.r = Range(settings['r'])
		self.b = Range(settings['b'])
		self.x0 = tk.DoubleVar(value = settings['x0'])
		self.n_iter = tk.IntVar(value = settings['n_iter'])
		self.n_draw = tk.IntVar(value = settings['n_draw'])


class Data():
	"""
	Хранит настройки для выбора нужной функции и указания параметров в UI.

	Attributes:
		is_f1 (tk.BooleanVar): Рассчитывать ли функцию №1?
		is_f2 (tk.BooleanVar): Рассчитывать ли функцию №2?
		f (Formula): Настройки параметров функции
		delay (tk.IntVar): Время на задержку отрисовки (мс)
		charts_num (tk.IntVar): Номер комбинации графиков для отображения
	"""
	def __init__(self, is_f1: bool, is_f2: bool, settings: dict,
			delay: int, charts_num: int):
		"""
		Устанавливает значения параметров в UI по-умолчанию.

		Attributes:
			is_f1 (bool): Рассчитывать ли функцию №1?
			is_f2 (bool): Рассчитывать ли функцию №2?
			settings (dict): Настройки параметров функции
			delay (tk.IntVar): Время на задержку отрисовки (мс)
			charts_num (tk.IntVar): Номер комбинации графиков для отображения
		"""
		self.is_f1 = tk.BooleanVar(value = is_f1)
		self.is_f2 = tk.BooleanVar(value = is_f2)
		self.f = Formula(settings)
		self.delay = tk.IntVar(value = delay)
		self.charts_num = tk.IntVar(value = charts_num)
	
	def set_formula(self, settings: dict):
		"""
		Обновляет значения параметров расчёта согласно словарю настроек.
		
		Attributes:
			settings (dict): Словарь настроек
		"""
		self.is_f1.set(settings['f1'])
		self.is_f2.set(settings['f2'])
		self.f.r.begin.set(settings['r'][0])
		self.f.r.end.set(settings['r'][1])
		self.f.r.step.set(settings['r'][2])
		self.f.b.begin.set(settings['b'][0])
		self.f.b.end.set(settings['b'][1])
		self.f.b.step.set(settings['b'][2])
		self.f.x0.set(settings['x0'])
		self.f.n_iter.set(settings['n_iter'])
		self.f.n_draw.set(settings['n_draw'])


class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
	"""Переопределяет положения меню для графиков."""
	def __init__(self, canvas, window):
		"""Переопределяет положения меню для графиков."""
		super().__init__(canvas, window, pack_toolbar = False)

	def _Button(self, text, image_file, toggle, command):
		"""Переопределяет кнопки панели инструментов в вертикальном направлении."""
		b = super()._Button(text, image_file, toggle, command)
		b.pack(side = tk.TOP) # кнопка переупаковки в вертикальном направлении
		return b

	def _Spacer(self):
		"""Переопределяет на вертикальный разделитель."""
		s = tk.Frame(self, width = 26, relief = tk.RIDGE, bg='DarkGray', padx = 2)
		s.pack(side = tk.TOP, pady = 5) # упаковать в вертикальном направлении
		return s
	
	def set_message(self, _):
		"""Убирает отображение позиции курсора."""
		pass