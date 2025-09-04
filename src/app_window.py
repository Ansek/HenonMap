import tkinter as tk
from threading import Timer
from tkinter.ttk import Progressbar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.settings import Settings
from src.controls import Data, VerticalNavigationToolbar2Tk
from src.calculations import NX, RX, RX_XX_NX, XX, XX_NX, Calculator
from src.help_window import Help
from src.plots import *


class App(tk.Tk):
	"""Основное окно приложения."""
	def __init__(self, save_dir: str):
		"""
		Основное окно приложения.
		
		Attributes:
			save_dir (str): Путь каталога для сохранения промежуточных файлов.
		"""
		super().__init__()
		self.save_dir = save_dir
		# Установка заголовка, размеров и положения окна
		self.wm_title('Отображение Эно')
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()
		w = w//2 # Середина экрана
		h = h//2
		w = w - 640 # Смещение от середины
		h = h - 360
		self.geometry('1280x720+{}+{}'.format(w, h))
		self.state('zoomed')
		self.settings = Settings(save_dir)
		# Установка значений по умолчанию
		self.data = Data(is_f1=True, is_f2=True,
			settings=self.settings['defaults'][0],
			delay=self.settings['delay_time'],
			charts_num=RX_XX_NX)
		self.anim = None # Для хранения объекта анимации
		self.is_calc = tk.BooleanVar() # Для возможности завершения вычисления
		self.pb = { # Информация для прогресс-бара
			'value': tk.IntVar(), # Текущее значение
			'max': tk.IntVar(), # Максимальное значение
			'status': tk.StringVar(), # Поясняющий текст
			'is_draw': False # Флаг, что есть точки для отрисовки
		}
		self.pb['max'].trace_add("write", self.update_max) # Функция обновления
		# Инициализация графика
		self.fig = Figure()
		self.fig.subplots_adjust(left = 0.09, bottom = 0.07, right = 0.97, top = 0.94, wspace = 0.35, hspace = 0.38)
		# Создание правого бокового меню
		self.menu = tk.Frame(master = self, width = 250, relief = tk.RIDGE, padx = 2)
		self.menu.pack(side = tk.RIGHT, fill = tk.Y)
		self.menu.rowconfigure(index=[1, 4, 1], weight = 1)
		self.menu.rowconfigure(index=[0, 3], weight = 10000)
		self.menu.rowconfigure(index = 2, weight = 1000000)
		# Кнопка должна блокироваться, поэтому добавлена перед регистрацией
		self.menu_btns = tk.Frame(self.menu)
		self.b1 = tk.Button(self.menu_btns)
		# Объекты для обеспечения контроля ввода
		self.empty_els = [] # Массив для хранения пустых полей
		vcmdi = (self.register(self.validate_int), '%P', '%W')
		vcmdf = (self.register(self.validate_float), '%P', '%W')
		# Добавление графика на форму
		self.canvas = FigureCanvasTkAgg(self.fig, master = self)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side = tk.RIGHT, fill = tk.BOTH, expand = 1)
		# Добавление меню графика на форму
		self.toolbar = VerticalNavigationToolbar2Tk(self.canvas, self)
		self.toolbar.update()
		self.toolbar.pack(side = tk.LEFT, fill = tk.Y)
		# Выбор формулы
		self.formula = tk.Frame(self.menu)
		self.formula.grid(row = 0, sticky="nw")
		self.fl = tk.Label(self.formula, text='Отображать значения для формул:')
		self.fl.pack(anchor = tk.W)
		self.c1 = tk.Checkbutton(self.formula, text='1) x[n+1]=rx[n](1-x[n])-bx[n-1]', variable = self.data.is_f1)
		self.c1.pack(anchor = tk.W)
		self.c2 = tk.Checkbutton(self.formula, text='2) x[n+1]=1-rx[n]^2+y[n]\ny[n+1]=bx[n]', variable = self.data.is_f2, justify = tk.LEFT)
		self.c2.pack(anchor = tk.W)
		# Параметры для функции
		self.params = tk.Frame(self.menu)
		self.params.grid(row = 1, sticky="nw", pady = 5)
		# Ввод параметров
		self.ol = tk.Label(self.params, text='Параметры:')
		self.ol.pack(anchor = tk.W)
		self.il = tk.Label(self.params, text='        [начало]   [конец]     [шаг]')
		self.il.pack(anchor = tk.W)
		TXT_WIDTH = 8
		# r
		self.rf = tk.Frame(self.params)
		self.rf.pack(anchor = tk.W)
		self.rl = tk.Label(self.rf, text='r = ')
		self.rl.pack(side = tk.LEFT)
		self.rb = tk.Entry(self.rf, textvariable = self.data.f.r.begin, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.rb.pack(side = tk.LEFT)
		self.re = tk.Entry(self.rf, textvariable = self.data.f.r.end, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.re.pack(side = tk.LEFT)
		self.rs = tk.Entry(self.rf, textvariable = self.data.f.r.step, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.rs.pack(side = tk.LEFT)
		# b
		self.bf = tk.Frame(self.params)
		self.bf.pack(anchor = tk.W)
		self.bl = tk.Label(self.bf, text='b = ')
		self.bl.pack(side = tk.LEFT)
		self.bb = tk.Entry(self.bf, textvariable = self.data.f.b.begin, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.bb.pack(side = tk.LEFT)
		self.be = tk.Entry(self.bf, textvariable = self.data.f.b.end, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.be.pack(side = tk.LEFT)
		self.bs = tk.Entry(self.bf, textvariable = self.data.f.b.step, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.bs.pack(side = tk.LEFT)
		# Установка начального значения
		self.x0f = tk.Frame(self.params)
		self.x0f.pack(anchor = tk.W)
		self.x0l = tk.Label(self.x0f, text='x[0] = ', justify = tk.LEFT)
		self.x0l.pack(side = tk.LEFT)
		self.x0 = tk.Entry(self.x0f, textvariable = self.data.f.x0, width = TXT_WIDTH, validate='key', validatecommand = vcmdf)
		self.x0.pack(side = tk.LEFT)
		# Установка шагов итерации
		self.nf = tk.Frame(self.params)
		self.nf.pack(anchor = tk.W)
		self.nil = tk.Label(self.nf, text='Количество итераций для\nдостижения устойчивого значения:', justify = tk.LEFT)
		self.nil.grid(row = 0, column = 0, sticky = tk.W)
		self.ni = tk.Entry(self.nf, textvariable = self.data.f.n_iter, width = TXT_WIDTH, validate='key', validatecommand = vcmdi)
		self.ni.grid(row = 0, column = 1)
		self.ndl = tk.Label(self.nf, text='Количество итераций для\nотрисовки графиков:', justify = tk.LEFT)
		self.ndl.grid(row = 1, column = 0, sticky = tk.W)
		self.nd = tk.Entry(self.nf, textvariable = self.data.f.n_draw, width = TXT_WIDTH, validate='key', validatecommand = vcmdi)
		self.nd.grid(row = 1, column = 1)
		# Кнопки для установки значения по умолчанию
		self.dl = tk.Label(self.params, text='Установка значений по умолчанию:')
		self.dl.pack(anchor = tk.W)
		self.btn_params = tk.Frame(self.menu, highlightbackground='gray', highlightthickness = 1)
		self.btn_params.grid(row = 2, sticky="nsew")
		# Добавление прокрутки
		self.canvas_btn = tk.Canvas(self.btn_params, width = 235)
		self.vsb = tk.Scrollbar(self.btn_params, command = self.canvas_btn.yview)
		self.btn_params.grid_rowconfigure(0, weight = 1)
		self.btn_params.grid_columnconfigure(0, weight = 1)
		self.canvas_btn.configure(yscrollcommand = self.vsb.set)
		self.canvas_btn.grid(row = 0, column = 0, sticky='nsew')
		self.vsb.grid(row = 0, column = 1, sticky='ns')
		#Добавление кнопок
		self.bf = tk.Frame(self.canvas_btn)
		for d in self.settings['defaults']:
			db = tk.Button(self.bf, text = d['name'], width = 32, command = lambda d = d: self.data.set_formula(d))
			db.pack(fill = tk.X, padx = 1, pady = 1)
		self.canvas_btn.create_window(0, 0, anchor='nw', window = self.bf)
		self.canvas_btn.bind('<Configure>', lambda event:
			self.canvas_btn.configure(scrollregion = self.canvas_btn.bbox('all')))
		self.canvas_btn.bind_all('<MouseWheel>', self.on_mouse_wheel)
		# Параметры для отрисовки
		self.gparams = tk.Frame(self.menu)
		self.gparams.grid(row = 3, sticky="nw", padx = 1, pady = 3)
		# Установка задержки
		self.tf = tk.Frame(self.gparams)
		self.tf.pack(anchor = tk.W)
		self.tl = tk.Label(self.tf, text='Длина задержки отрисовки:', justify = tk.LEFT)
		self.tl.pack(side = tk.LEFT)
		self.t = tk.Entry(self.tf, textvariable = self.data.delay, width = TXT_WIDTH, validate='key', validatecommand = vcmdi)
		self.t.pack(side = tk.LEFT)
		self.t = tk.Label(self.tf, text='мс', justify = tk.LEFT)
		self.t.pack(side = tk.LEFT)
		# Выбор отображения
		self.gl = tk.Label(self.gparams, text='Выбор графика для отображения:', justify = tk.LEFT)
		self.rg1 = tk.Radiobutton(self.gparams, text='График зависимостей (x[n], x[n+1] от n)', variable = self.data.charts_num, value = NX)
		self.rg1.pack(anchor = tk.W)
		self.rg2 = tk.Radiobutton(self.gparams, text='Фазовый портрет (x[n+1] от x[n])', variable = self.data.charts_num, value = XX)
		self.rg2.pack(anchor = tk.W)
		self.rg3 = tk.Radiobutton(self.gparams, text='Бифуркационная диаграмма (x[n] от r)', variable = self.data.charts_num, value = RX)
		self.rg3.pack(anchor = tk.W)
		self.rg4 = tk.Radiobutton(self.gparams, text='Фазовый портрет и график зависимостей', variable = self.data.charts_num, value = XX_NX)
		self.rg4.pack(anchor = tk.W)
		self.rg5 = tk.Radiobutton(self.gparams, text='Все графики', variable = self.data.charts_num, value = RX_XX_NX)
		self.rg5.pack(anchor = tk.W)
		# Кнопка запуска/завершения анимации
		self.b1_text = tk.StringVar(value='Отобразить')
		self.b1.configure(textvariable = self.b1_text, command = lambda: self.draw())
		self.b1.pack(fill = tk.X, padx = 1)
		# Кнопка приостановки/продолжения анимации
		self.b2_text = tk.StringVar(value='Пауза')
		self.b2 = tk.Button(self.menu_btns, textvariable = self.b2_text, command = lambda: self.pause())
		self.b2.configure(state = tk.DISABLED)
		self.b2.pack(fill = tk.X, pady = 1)
		self.b3 = tk.Button(self.menu_btns, text="Справка", command = lambda: Help(self).grab_set())
		self.b3.pack(fill = tk.X, pady = 1)
		self.st = tk.Label(self.menu_btns, textvariable = self.pb['status'])
		self.st.pack(anchor = tk.W, pady = 1)
		self.pbar = Progressbar(self.menu_btns, orient='horizontal', mode='determinate', variable = self.pb['value'], length = 250)
		self.pbar.pack(fill = tk.X, pady = 1)
		self.menu_btns.grid(row = 4, sticky="nsew", padx = 1)

	def set_state(self, state):
		"""
		Устанавливает состояние активности для нескольких элементов.

		Args:
			state: tk.NORMAL | tk.DISABLED
		"""
		# Перебор всех дочерних элементов для установки параметра
		for frame in [self.formula, self.params, self.gparams, self.bf]:
			for child in frame.winfo_children():
				if isinstance(child, tk.Frame):
					for child2 in child.winfo_children():
						child2.configure(state = state)
				else:
					child.configure(state = state)

	def del_anim(self):
		"""Выполнение предварительных действий перед удалением объекта анимации."""
		# Были ли получены хоть какие-то точки
		if self.pb['is_draw']:
			if hasattr(self, 'anim'):
				self.anim.del_new_points() # Убрать точки, показывающих процесс отрисовки
				del self.anim # Удаление объекта анимации
			self.pb['status'].set('Завершено')
		else:
			self.pb['status'].set('Прекращено')
		self.pb['value'].set(0)
		self.canvas.draw()

	def run_anim(self, res):
		"""Запускает анимацию после выполнения вычислений."""
		self.b1_text.set('Завершить анимацию')
		self.pb['status'].set('Анимирование графика (3/3)')
		self.pb['value'].set(0)
		self.pb['max'].set(self.data.f.n_draw.get())
		self.b2.configure(state = tk.NORMAL)
		self.anim = SubplotAnimation(self.fig, self.data, res, self.pb, self.end_anim, self.settings)

	def end_anim(self):
		"""Выполняетдействия после завершения анимации."""
		self.b1_text.set('Отобразить') # Установка подписей и состояния
		self.b2_text.set('Пауза')
		self.set_state(tk.NORMAL)
		self.b2.configure(state = tk.DISABLED)
		Timer(0.5, self.del_anim).start() # Обновление графика через 0.5 сек (легенды)

	def draw(self):
		"""Действия после нажатия кнопки Отобразить/Завершить."""
		# Запуск вычислений
		if self.b1_text.get() == 'Отобразить':
			# Подготовка прогресс-бара
			self.pb['value'].set(0)
			self.pb['status'].set('Инициализация')
			self.pb['is_draw'] = False
			# Установка подписей и состояния
			self.b1_text.set('Завершить вычисление')
			self.set_state(tk.DISABLED)
			# Запуск вычисления
			self.is_calc.set(True)
			Calculator(self.data, self.pb, self.is_calc,
			  	self.save_dir, self.run_anim)
		# Принудительное прекращение вычислений
		elif self.is_calc.get():
			self.is_calc.set(False)
			# Если нет никаких точек для отрисовки
			if not self.pb['is_draw']:
				self.end_anim()
		# Принудительное прекращение анимирования
		else:
			if hasattr(self, 'anim') and self.anim.event_source is not None:
				self.anim.pause() # то останавливаем
			self.end_anim()

	def pause(self):
		"""Действия после нажатия кнопки Пауза/Продолжить."""
		if hasattr(self, 'anim'):
			if self.b2_text.get() == 'Пауза':
				self.anim.pause()
				self.b2_text.set('Продолжить')
			else:
				self.anim.resume()
				self.b2_text.set('Пауза')

	def on_mouse_wheel(self, event):
		"""Событие прокрутки колеса мыши."""
		self.canvas_btn.yview_scroll(-1*int(event.delta/120), 'units')

	def value_is_empty(self, value, el):
		"""
		Действие, если значение оказалось незаполненным.

		Args:
			value int|float: Проверяемое значение.
			el: Элемент управления для блокировки.
		"""
		# Добавление элемента, если у него пустое значение и его нет в списке
		if value == '' and el not in self.empty_els:
			self.empty_els.append(el)
			self.nametowidget(el).configure(highlightbackground='red', highlightthickness = 1)
		# и его удаление, если появилось значение
		elif value != '' and el in self.empty_els:
			self.empty_els.remove(el)
			self.nametowidget(el).configure(highlightthickness = 0)
		# Блокировка и разблокировка в зависимости от количества пустых полей
		if len(self.empty_els) > 0:
			self.b1.configure(state = tk.DISABLED)
		else:
			self.b1.configure(state = tk.NORMAL)

	def validate_int(self, value, el):
		"""
		Ограничивает вводом только целого числа.
		
		Args:
			value int|float: Проверяемое значение.
			el: Элемент управления для блокировки.
		"""
		self.value_is_empty(value, el)
		if value == '': # Чтобы разрешить удаление символа
			value = 0
		try:
			i = int(value)
			return i >= 0
		except:
			return False

	# Ограничение на ввод вещественного числа
	def validate_float(self, value, el):
		"""
		Ограничивает вводом только вещественного числа.
		
		
		Args:
			value int|float: Проверяемое значение.
			el: Элемент управления для блокировки.
		"""
		self.value_is_empty(value, el)
		if value == '': # Чтобы разрешить удаление символа
			value = 0
		try:
			float(value)
			return True
		except:
			return False

	def update_max(self, *args):
		"""Обновление максимального значения ProgressBar."""
		self.pbar.configure(maximum = self.pb['max'].get())