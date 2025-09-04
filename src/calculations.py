import os
import numpy as np
import tkinter as tk
from threading import Thread
from tkinter.messagebox import askyesno

from src.controls import Data

# Перечисление доступных графиков
RX_XX_NX = 0 # Все графики
XX_NX = 1	# Фазовый портрет и график зависимостей
RX = 2		# Бифуркационная диаграмма (x[n] от r)
XX = 3		# Фазовый портрет (x[n+1] от x[n])
NX = 4		# График зависимостей (x[n], x[n+1] от n)


class CalcData:
	"""
	Хранит вспомогательные данные для расчётов.

	Attributes:
		error (str): Хранит значения, при которых произошла ошибка (лог)
		i (int): Значение текущей операции
	"""

	def __init__(self, save_dir: str):
		"""Инициализирует хранилище функций для расчётов.
		
		Args:
			save_dir (str): Каталог для сохранения файлов
		"""
		self.save_dir = save_dir
		self.error = ''
		self.i = 0

	def run(self, f, name: str, x0: np.array, x1: np.array,
	    r: np.array, b: np.array) -> np.array:
		"""
		Запускает расчёт функции с проверкой на уход результатов в бесконечность.

		Args:
			f (method): Функция расчёта
			name (str): Имя функции
			x0 (np.array): Предыдущее значения x[n-1]
			x1 (np.array): Текущее значения x[n]
			r, b (np.array): Коэффициенты функции
		
		Returns:
			np.array: Новые значения x[n+1]
		"""
		res = f(x0, x1, r, b)
		if np.isinf(res).any():
			j = abs(res) == np.inf
			for x0j, x1j, rj, bj in zip(x0, x1, r, b):
				self.error += '%s: i = %d\tx0 = %.4e\t\tx1 = %.4e\tr = %.4f\t\tb = %.4f\n' % (name, self.i, x0j, x1j, rj, bj)
			res[j] = 0
		return res

	def f1(self, x0: np.array, x1: np.array,
			r: np.array, b: np.array) -> np.array:
		"""
		Формула из методического указания:  
		x[n+1] = rx[n](1 - x[n]) - bx[n-1]

		Args:
			f (method): Функция расчёта
			name (str): Имя функции
			x0 (np.array): Предыдущее значения x[n-1]
			x1 (np.array): Текущее значения x[n]
			r, b (np.array): Коэффициенты функции
		
		Returns:
			np.array: Новые значения x[n+1]
		"""
		lf1 = lambda x0, x1, r, b: r*x1*(1 - x1) - b * x0
		return self.run(lf1, 'f1', x0, x1, r, b)

	def f2(self, x0: np.array, x1: np.array,
			r: np.array, b: np.array) -> np.array:
		"""
		Формула из стороннего источника:  
		x[n+1] = 1 - rx[n]^2 + y[n]  
		y[n+1] = bx[n]
		
		Args:
			f (method): Функция расчёта
			name (str): Имя функции
			x0 (np.array): Предыдущее значения x[n-1]
			x1 (np.array): Текущее значения x[n]
			r, b (np.array): Коэффициенты функции
		
		Returns:
			np.array: Новые значения x[n+1]
		"""
		lf2 = lambda x0, x1, r, b: 1 - r * x1**2 + b * x0
		return self.run(lf2, 'f2', x0, x1, r, b)
	
	def show_error(self):
		"""Оповещает об обнаруженных ошибках вычисления."""
		if self.error != '':
			result = askyesno('Подтверждение операции', 'В ходе вычислений были получены исключения.\nОткрыть блокнот c данными параметрами?')
			if result:
				fn = os.path.join(self.save_dir, 'error.txt')
				with open(fn, 'w', encoding='utf-8') as f:
					f.write(self.error)
				# Открытие в блокноте
				os.system(f'notepad.exe {fn}')
	
	def inc(self):
		"""Увеличение индекса текущего вычисления."""
		self.i += 1


class Calculator:
	"""
	Управляет процессом вычисления значений.

	Attributes:
		data (Data): Параметры для вычисления
		pb (dict): Компоненты для отображения информации о прогрессе вычисления
		is_calc (tk.BooleanVar): Флаг для преждевременного прекращения работы
		next_func (method): Функция, запускаемая после завершения вычисления
		is_f1 (bool): Рассчитывать ли функцию №1?
		is_f2 (bool): Рассчитывать ли функцию №2?
		n_iter (int): Количество итераций для вычисления.
		n_draw (int): Количество итераций для отрисовки.
	"""

	def __init__(self, data: Data, pb: dict, is_calc: tk.BooleanVar,
			save_dir: str, next_func):
		"""
		Управляет процессом вычисления значений.

		Attributes:
			data (Data): Параметры для вычисления
			pb (dict): Компоненты для отображения информации о прогрессе вычисления
			is_calc (tk.BooleanVar): Флаг для преждевременного прекращения работы
			save_dir (str): Каталог для сохранения файлов
			next_func (method): Функция, запускаемая после завершения вычисления
		"""
		# Флаги, какие функции рассчитывать
		self.is_f1 = data.is_f1.get()
		self.is_f2 = data.is_f2.get()
		# Количество итераций
		self.n_iter = data.f.n_iter.get()
		self.n_draw = data.f.n_draw.get()
		# Сохранение функции, которая должна запустится следующей
		self.next_func = next_func
		self.is_calc = is_calc
		self.pb = pb
		# Подготовка параметров для функций
		r = data.f.r
		b = data.f.b
		arr_n = np.arange(self.n_iter + 1, self.n_iter + self.n_draw + 1, 1)
		arr_r = np.arange(r.begin.get(), r.end.get()+0.000001, r.step.get())
		arr_b = np.arange(b.begin.get(), b.end.get()+0.000001, b.step.get())
		if arr_r.size == 0:
			arr_r = np.array([r.begin.get()])
		if arr_b.size == 0:
			arr_b = np.array([b.begin.get()])
		self.Nbr = arr_r.size * arr_b.size
		self.Nbrn = (arr_n.size + 2) * self.Nbr # +1 для x[i+2], i = n - 1
		# Дублирование
		# n1 n1 n1 n1 n1 n1
		# r1 r1 r1 r2 r2 r2
		# b1 b2 b3 b1 b2 b3
		self.n = np.repeat(arr_n, self.Nbr)
		self.r = np.repeat(arr_r, arr_b.size)
		self.b = np.array([])
		for _ in range(arr_r.size):
			self.b = np.hstack([self.b, arr_b])
		# Если строится бифуркационная диаграмма
		if data.charts_num.get() == RX_XX_NX or data.charts_num.get() == RX:
			self.rn = np.array([])
			for _ in range(arr_n.size):
				self.rn = np.hstack([self.rn, self.r])
		# Резервирование места для x[n] и x[n-1]
		if self.is_f1:
			self.x_f1 = np.zeros(self.Nbrn)
			self.x0_f1 = np.zeros(self.Nbr) + data.f.x0.get() # Инициализация X[0]
			self.x1_f1 = self.x0_f1.copy()
		if self.is_f2:
			self.x_f2 = np.zeros(self.Nbrn)
			self.x0_f2 = np.zeros(self.Nbr) + data.f.x0.get() # Инициализация X[0]
			self.x1_f2 = self.x0_f2.copy()
		calc = CalcData(save_dir)
		# Создание объекта для вычислений
		if self.is_calc.get():
			thread = Thread(target = self.run, args=(calc, ))
			thread.start()

	def run(self, calc: CalcData):
		"""
		Запускает процесс вычисления.

		Attributes:
			calc (CalcData): Параметры и данные для вычисления
		"""
		# Получение устойчивых предельных значений
		if self.is_f1 or self.is_f2:
			self.pb['status'].set('Достижение устойчивых значений (1/3)')
			self.pb['value'].set(0)
			self.pb['max'].set(self.n_iter + 1)
			# Итерации без вывода
			for i in range(self.pb['max'].get()):
				if self.is_calc.get() == False: # Для принудительного прекращения вычислений
					return
				if self.is_f1:
					temp = self.x1_f1
					self.x1_f1 = calc.f1(self.x0_f1, self.x1_f1, self.r, self.b)
					self.x0_f1 = temp
				if self.is_f2:
					temp = self.x1_f2
					self.x1_f2 = calc.f2(self.x0_f2, self.x1_f2, self.r, self.b)
					self.x0_f2 = temp
				calc.inc() # Актуальный номер для отчёта об ошибке
				self.pb['value'].set(i)
			# Инициализация индексов (N0 x[n-1] N1 x[n] N2 x[n+1] N3)
			self.init_N()
			# Установка начальных значений
			if self.is_f1:
				self.x_f1[self.N0:self.N1] = self.x0_f1 # x[n-1]
				self.x_f1[self.N1:self.N2] = self.x1_f1 # x[n]
			if self.is_f2:
				self.x_f2[self.N0:self.N1] = self.x0_f2 # x[n-1]
				self.x_f2[self.N1:self.N2] = self.x1_f2 # x[n]
			# Расчёт значений для вывода на график
			self.pb['status'].set('Расчёт значений для отрисовки (2/3)')
			self.pb['value'].set(0)
			self.pb['max'].set(self.n_draw)
			self.pb['is_draw'] = True
			for i in range(self.n_draw):
				if self.is_calc.get() == False: # Для принудительного прекращения вычислений
					break
				if self.is_f1:
					x0 = self.x_f1[self.N0:self.N1]
					x1 = self.x_f1[self.N1:self.N2]
					self.x_f1[self.N2:self.N3] = calc.f1(x0, x1, self.r, self.b)
				if self.is_f2:
					x0 = self.x_f2[self.N0:self.N1]
					x1 = self.x_f2[self.N1:self.N2]
					self.x_f2[self.N2:self.N3] = calc.f2(x0, x1, self.r, self.b)
				calc.inc() # Актуальный номер для отчёта об ошибке
				self.pb['value'].set(i)
				self.next_N() # Сдвиг индексов
			# Сброс индексов для последовательного отображения
			self.init_N()
		calc.show_error()
		# Определение границ графика
		self.x_lim = np.array([])
		# Определение границ графика
		if self.is_f1 and self.is_f2:
			self.x_lim = [np.amin([self.x_f1, self.x_f2]), np.amax([self.x_f1, self.x_f2])]
		elif self.is_f1:
			self.x_lim = [np.amin(self.x_f1), np.amax(self.x_f1)]
		elif self.is_f2:
			self.x_lim = [np.amin(self.x_f2), np.amax(self.x_f2)]
		else:
			self.x_lim = [1, 1]
		# Попытка исправить проблему с axis
		if self.x_lim[0] < -1.5E300:
			self.x_lim[0] = -1.5E300
		if self.x_lim[1] > 1.5E300:
			self.x_lim[1] = 1.5E300
		self.n_lim = [self.n[0], self.n[self.n.size - 1]]
		self.r_lim = [self.r[0], self.r[self.r.size - 1]]
		# Запуск следующей функции
		self.is_calc.set(False)
		self.next_func(self)

	def init_N(self):
		"""
		Инициализация индексов по диапазонам
		N0 x[n-1] N1 x[n] N2 x[n+1] N3
		"""
		self.N0 = 0
		self.N1 = self.Nbr
		self.N2 = self.N1 + self.Nbr
		self.N3 = self.N2 + self.Nbr

	def next_N(self):
		""" Увеличение индексов на заданный шаг."""
		self.N0 += self.Nbr
		self.N1 += self.Nbr
		self.N2 += self.Nbr
		self.N3 += self.Nbr

	def get_n(self):
		"""Получение фрагмента данных n."""
		return self.n[:self.N1]

	def get_xn_f1(self):
		"""Получение фрагмента данных x[n] для функции №1."""
		return self.x_f1[:self.N1]

	def get_xn1_f1(self):
		"""Получение фрагмента данных x[n+1] для функции №1."""
		return self.x_f1[self.Nbr:self.N2]

	def get_xn_f2(self):
		"""Получение фрагмента данных x[n] для функции №2."""
		return self.x_f2[:self.N1]

	def get_xn1_f2(self):
		"""Получение фрагмента данных x[n+1] для функции №2."""
		return self.x_f2[self.Nbr:self.N2]

	def get_r(self):
		"""Получение фрагмента данных r."""
		return self.rn[:self.N1]

	def last_xn_f1(self):
		"""Получение последних данных x[n] для функции №1."""
		return self.x_f1[self.N0:self.N1]

	def last_xn1_f1(self):
		"""Получение последних данных x[n+1] для функции №1."""
		return self.x_f1[self.N1:self.N2]

	def last_xn_f2(self):
		"""Получение последних данных x[n] для функции №2."""
		return self.x_f2[self.N0:self.N1]

	def last_xn1_f2(self):
		"""Получение фрагмента данных x[n+1] для функции №2."""
		return self.x_f2[self.N1:self.N2]

	def last_r(self):
		"""Получение последних данных r."""
		return self.rn[self.N0:self.N1]