from matplotlib.animation import TimedAnimation

from src.controls import Data
from src.settings import Settings
from src.calculations import NX, RX, XX, XX_NX, Calculator

class Plot():
	"""
	Управляет отдельным графиком.

	Attributes:
		axis (matplotlib.pyplot.Axis): Объект для отображения графика
		data (Data): Исходные данные
		res (Calculator): Объект выполнивший вычисление
		key (str): Индекс, по которому можно получить доступ к настройкам
		f1_lines (list): # Для хранения линий функции №1
		f2_lines (list): # Для хранения линий функции №2
		settings (Settings) # Глобальные настройки приложения
	"""
	def __init__(self, axis, data: Data,
			res: Calculator, key: str, settings: Settings):
		"""
		Управляет отдельным графиком.

		Attributes:
			axis (matplotlib.pyplot.Axis): Объект для отображения графика
			data (Data): Исходные данные
			res (Calculator): Объект выполнивший вычисление
			key (str): Индекс, по которому можно получить доступ к настройкам
			settings (Settings) # Глобальные настройки приложения
		"""
		self.axis = axis # Объект для отображения графика
		self.data = data # Данные с формы
		self.res = res # Результаты вычислений функции
		self.key = key # Индекс, по которому можно получить доступ к настройкам
		self.f1_lines = [] # Для хранения линий функции №1
		self.f2_lines = [] # Для хранения линий функции №2
		self.settings = settings

	def get_two_lines(self, s) -> list:
		"""Получает линии для отрисовки."""
		lines = []
		line, = self.axis.plot([], [], s['marker1'], color = s['color1'],
			markersize = s['markersize1'], label = s['label1'])
		lines.append(line)
		line, = self.axis.plot([], [], s['marker2'], color = s['color2'],
			markersize = s['markersize2'], label = s['label2'])
		lines.append(line)
		return lines
	
	def create_lines(self) -> list:
		"""Формирование линий."""
		lines = []
		if self.data.is_f1.get():
			self.f1_lines = self.get_two_lines(self.settings[self.key]['f1'])
			lines.extend(self.f1_lines)
		if self.data.is_f2.get():
			self.f2_lines = self.get_two_lines(self.settings[self.key]['f2'])
			lines.extend(self.f2_lines)
		# Настройка положения легенды
		self.axis.legend(loc = self.settings[self.key]['legend_loc'])
		return lines
	
	def set_lim(self, x_lim, y_lim, s):
		"""Установка границ отображения"""
		kx = s['coef_xlim'] * (x_lim[1] - x_lim[0])
		ky = s['coef_ylim'] * (y_lim[1] - y_lim[0])
		self.axis.set_xlim(x_lim[0] - kx, x_lim[1] + kx)
		self.axis.set_ylim(y_lim[0] - ky, y_lim[1] + ky)

	def del_new_points(self):
		"""Удаление точек, показывающих процесс отрисовки."""
		if self.data.is_f1.get():
			self.f1_lines[1].remove()
		if self.data.is_f2.get():
			self.f2_lines[1].remove()
		# Обновление легенды
		self.axis.legend(loc = self.settings[self.key]['legend_loc'])


class PlotNX(Plot):
	"""
	График зависимостей (x[n], x[n+1] от n).

	Attributes:
		axis (matplotlib.pyplot.Axis): Объект для отображения графика
		data (Data): Исходные данные
		res (Calculator): Объект выполнивший вычисление
		key (str): Индекс, по которому можно получить доступ к настройкам
		f1_lines (list): # Для хранения линий функции №1
		f2_lines (list): # Для хранения линий функции №2
		settings (Settings) # Глобальные настройки приложения
	"""

	def __init__(self, axis, data, res, settings):
		"""
		График зависимостей (x[n], x[n+1] от n).

		Attributes:
			axis (matplotlib.pyplot.Axis): Объект для отображения графика
			data (Data): Исходные данные
			res (Calculator): Объект выполнивший вычисление
			settings (Settings) # Глобальные настройки приложения
		"""
		super().__init__(axis, data, res, 'NX', settings)
		# Установка подписей
		axis.set_title('График зависимостей\n(x[n], x[n+1] от n)',
				fontsize = self.settings['fontsize'])
		axis.set_xlabel('n', fontsize = self.settings['fontsize'])
		axis.set_ylabel('x[n], x[n+1]', fontsize = self.settings['fontsize'])
		# Установка границ
		self.set_lim(res.n_lim, res.x_lim, self.settings['NX'])

	def update_lines(self):
		"""Обновление данных для отрисовки."""
		if self.data.is_f1.get():
			self.f1_lines[0].set_data(self.res.get_n(), self.res.get_xn_f1())
			self.f1_lines[1].set_data(self.res.get_n(), self.res.get_xn1_f1())
		if self.data.is_f2.get():
			self.f2_lines[0].set_data(self.res.get_n(), self.res.get_xn_f2())
			self.f2_lines[1].set_data(self.res.get_n(), self.res.get_xn1_f2())

	def del_new_points(self):
		"""Удаление точек, показывающих процесс отрисовки."""
		pass # Нет демонстрационных точек (процесс отрисовки) для удаления


class PlotXX(Plot):
	"""
	Фазовый портрет (x[n+1] от x[n]).

	Attributes:
		axis (matplotlib.pyplot.Axis): Объект для отображения графика
		data (Data): Исходные данные
		res (Calculator): Объект выполнивший вычисление
		key (str): Индекс, по которому можно получить доступ к настройкам
		f1_lines (list): # Для хранения линий функции №1
		f2_lines (list): # Для хранения линий функции №2
		settings (Settings) # Глобальные настройки приложения
	"""

	def __init__(self, axis, data, res, settings):
		"""
		Фазовый портрет (x[n+1] от x[n]).

		Attributes:
			axis (matplotlib.pyplot.Axis): Объект для отображения графика
			data (Data): Исходные данные
			res (Calculator): Объект выполнивший вычисление
			settings (Settings) # Глобальные настройки приложения
		"""
		super().__init__(axis, data, res, 'XX', settings)
		# Установка подписей
		axis.set_title('Фазовый портрет\n(x[n+1] от x[n])',
				fontsize = self.settings['fontsize'])
		axis.set_xlabel('x[n]', fontsize = self.settings['fontsize'])
		axis.set_ylabel('x[n+1]', fontsize = self.settings['fontsize'])
		# Установка границ
		self.set_lim(res.x_lim, res.x_lim, self.settings['XX'])

	def update_lines(self):
		"""Обновление данных для отрисовки."""
		if self.data.is_f1.get():
			self.f1_lines[0].set_data(self.res.get_xn_f1(), self.res.get_xn1_f1())
			self.f1_lines[1].set_data(self.res.last_xn_f1(), self.res.last_xn1_f1())
		if self.data.is_f2.get():
			self.f2_lines[0].set_data(self.res.get_xn_f2(), self.res.get_xn1_f2())
			self.f2_lines[1].set_data(self.res.last_xn_f2(), self.res.last_xn1_f2())


class PlotRX(Plot):
	"""
	Бифуркационная диаграмма (x[n] от r).

	Attributes:
		axis (matplotlib.pyplot.Axis): Объект для отображения графика
		data (Data): Исходные данные
		res (Calculator): Объект выполнивший вычисление
		key (str): Индекс, по которому можно получить доступ к настройкам
		f1_lines (list): # Для хранения линий функции №1
		f2_lines (list): # Для хранения линий функции №2
		settings (Settings) # Глобальные настройки приложения
	"""

	def __init__(self, axis, data, res, settings):
		"""
		Бифуркационная диаграмма (x[n] от r).

		Attributes:
			axis (matplotlib.pyplot.Axis): Объект для отображения графика
			data (Data): Исходные данные
			res (Calculator): Объект выполнивший вычисление
			settings (Settings) # Глобальные настройки приложения
		"""
		super().__init__(axis, data, res, 'RX', settings)
		# Установка подписей
		axis.set_title('Бифуркационная диаграмма\n(x[n] от r)',
				fontsize = self.settings['fontsize'])
		axis.set_xlabel('r', fontsize = self.settings['fontsize'])
		axis.set_ylabel('x[n]', fontsize = self.settings['fontsize'])
		# Установка границ
		self.set_lim(res.r_lim, res.x_lim, self.settings['RX'])

	def update_lines(self):
		"""Обновление данных для отрисовки."""
		if self.data.is_f1.get():
			self.f1_lines[0].set_data(self.res.get_r(), self.res.get_xn_f1())
			self.f1_lines[1].set_data(self.res.last_r(), self.res.last_xn_f1())
		if self.data.is_f2.get():
			self.f2_lines[0].set_data(self.res.get_r(), self.res.get_xn_f2())
			self.f2_lines[1].set_data(self.res.last_r(), self.res.last_xn_f2())


class SubplotAnimation(TimedAnimation):
	"""
	Выполняет анимацию отрисовки графиков.

	Attributes:
		fig (matplotlib.pyplot.Figure):  Объект графика
		data (Data): Исходные данные  
		res (Calculator): Объект выполнивший вычисление
		pb (dict): Компоненты для отображения информации о прогрессе вычисления 
		end_anim (method): Для оповещения о завершении анимации
		settings (Settings): Глобальные настройки приложения
		n_draw (int): Сколько кадров отрисовывать
		self.axes (list): Список пространств для отрисовки
		self.lines (list): Список линий для обновления
	"""

	def __init__(self, fig, data: Data, res: Calculator,
			pb: dict, end_anim, settings):
		"""
		Выполняет анимацию отрисовки графиков.

		Attributes:
			fig (matplotlib.pyplot.Figure):  Объект графика
			data (Data): Исходные данные  
			res (Calculator): Объект выполнивший вычисление
			pb (dict): Компоненты для отображения информации о прогрессе вычисления 
			end_anim (method): Для оповещения о завершении анимации
			settings (Settings) # Глобальные настройки приложения
		"""
		self.fig = fig
		self.data = data
		self.res = res 
		self.pb = pb 
		self.end_anim = end_anim 
		self.n_draw = data.f.n_draw.get()
		# Определение количества графиков
		self.fig.clear()
		g = data.charts_num.get()
		self.axes = []
		if g == NX or g == XX or g == RX:
			axis1 = self.fig.add_subplot(1, 1, 1)
			if g == NX:
				self.axes.append(PlotNX(axis1, data, self.res, settings))
			elif g == XX:
				self.axes.append(PlotXX(axis1, data, self.res, settings))
			else:
				self.axes.append(PlotRX(axis1, data, self.res, settings))
		elif g == XX_NX:
			axis1 = self.fig.add_subplot(2, 1, 1)
			axis2 = self.fig.add_subplot(2, 1, 2)
			self.axes.append(PlotXX(axis1, data, self.res, settings))
			self.axes.append(PlotNX(axis2, data, self.res, settings))
		else:
			axis1 = self.fig.add_subplot(2, 2, 1)
			axis2 = self.fig.add_subplot(2, 2, 2)
			axis3 = self.fig.add_subplot(2, 1, 2)
			self.axes.append(PlotRX(axis1, data, self.res, settings))
			self.axes.append(PlotXX(axis2, data, self.res, settings))
			self.axes.append(PlotNX(axis3, data, self.res, settings))
		# Получение списка линий
		self.lines = []
		for axis in self.axes:
			self.lines.extend(axis.create_lines())
			TimedAnimation.__init__(self, fig,
				interval = data.delay.get(), repeat = False, blit = True)

	def _draw_frame(self, i):
		"""Обновление кадра (x[i] = x[n-1])."""
		# Вызов обработки каждого графика
		for axis in self.axes:
			axis.update_lines()
		self._drawn_artists = self.lines
		# Обновление ссылок на данные
		self.res.next_N()
		#Обновление прогресс-бара
		self.pb['value'].set(i)
		# Сигнал о завершении анимации
		if i == self.n_draw - 1:
			self.end_anim()

	def new_frame_seq(self) -> iter:
		"""Возвращает счетчик для определения количества кадров."""
		return iter(range(self.n_draw))

	def del_new_points(self):
		"""Удаление точек, показывающих процесс отрисовки."""
		for axis in self.axes:
			axis.del_new_points()