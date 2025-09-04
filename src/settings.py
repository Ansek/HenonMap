import os, json


SETTINGS = {
   'fontsize': 9,
   'delay_time': 1,
   'NX': {
	  'f1': {
		 'label1': '1) x[n]',
		 'color1': 'c',
		 'marker1': '-',
		 'markersize1': 0,
		 'label2': '1) x[n+1]',
		 'color2': 'b',
		 'marker2': '-',
		 'markersize2': 0
	  },
	  'f2': {
		 'label1': '2) x[n]',
		 'color1': 'darkorange',
		 'marker1': '-',
		 'markersize1': 0,
		 'label2': '2) x[n+1]',
		 'color2': 'r',
		 'marker2': '-',
		 'markersize2': 0
	  },
	  'coef_xlim': 0,
	  'coef_ylim': 0.05,
	  'legend_loc': 'upper right'
   },
   'XX': {
	  'f1': {
		 'label1': '1) old',
		 'color1': 'c',
		 'marker1': '.',
		 'markersize1': 3,
		 'label2': '1) new',
		 'color2': 'b',
		 'marker2': 'x',
		 'markersize2': 7.5
	  },
	  'f2': {
		 'label1': '2) old',
		 'color1': 'darkorange',
		 'marker1': '.',
		 'markersize1': 3,
		 'label2': '2) new',
		 'color2': 'r',
		 'marker2': 'x',
		 'markersize2': 7.5
	  },
	  'coef_xlim': 0.05,
	  'coef_ylim': 0.05,
	  'legend_loc': 'upper left'
   },
   'RX': {
	  'f1': {
		 'label1': '1) old',
		 'color1': 'c',
		 'marker1': '.',
		 'markersize1': 3,
		 'label2': '1) new',
		 'color2': 'b',
		 'marker2': 'x',
		 'markersize2': 7.5
	  },
	  'f2': {
		 'label1': '2) old',
		 'color1': 'darkorange',
		 'marker1': '.',
		 'markersize1': 3,
		 'label2': '2) new',
		 'color2': 'r',
		 'marker2': 'x',
		 'markersize2': 7.5
	  },
	  'coef_xlim': 0.05,
	  'coef_ylim': 0.05,
	  'legend_loc': 'lower left'
   },
   'defaults': [
	  {
		 'name': 'r = 1.4; b = 0.3',
		 'f1': True,
		 'f2': True,
		 'r': [1.4, 1.4, 0.1],
		 'b': [0.3, 0.3, 0.1],
		 'x0': 0,
		 'n_iter': 800,
		 'n_draw': 600
	  },
	  {
		 'name': 'r = 0..1.4; b = 0.3',
		 'f1': True,
		 'f2': True,
		 'r': [0, 1.4, 0.01],
		 'b': [0.3, 0.3, 0.1],
		 'x0': 0,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'r = 0..1.4; b = 0..0.4',
		 'f1': True,
		 'f2': True,
		 'r': [0, 1.4, 0.01],
		 'b': [0, 0.4, 0.1],
		 'x0': 0,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 3 (ошибки)',
		 'f1': True,
		 'f2': False,
		 'r': [3, 3, 0.01],
		 'b': [0.1, 0.1, 0.1],
		 'x0': 0.4,
		 'n_iter': 0,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 4',
		 'f1': True,
		 'f2': False,
		 'r': [4, 4, 0.01],
		 'b': [0.1, 0.1, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 0..4; b=0',
		 'f1': True,
		 'f2': False,
		 'r': [0, 4, 0.05],
		 'b': [0, 0, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 0..4; b=0.1',
		 'f1': True,
		 'f2': False,
		 'r': [0, 4, 0.05],
		 'b': [0.1, 0.1, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 0..4; b=0.2',
		 'f1': True,
		 'f2': False,
		 'r': [0, 4, 0.05],
		 'b': [0.2, 0.2, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'По варианту:  x[0] = 0.4; r = 0..4; b=0.3',
		 'f1': True,
		 'f2': False,
		 'r': [0, 4, 0.05],
		 'b': [0.3, 0.3, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  },
	  {
		 'name': 'x[0] = 0.4; r = 0..4; b=0.4 (долго+ошибки)',
		 'f1': True,
		 'f2': False,
		 'r': [0, 4, 0.05],
		 'b': [0.4, 0.4, 0.1],
		 'x0': 0.4,
		 'n_iter': 800,
		 'n_draw': 300
	  }
   ]
}


class Settings:
	"""Загружает настройки из файла."""

	def __init__(self, save_dir: str, filename = 'settings.json'):
		"""Загружает настройки из файла. Если его нет,
		то предварительно создает его шаблон.

		Attributes:
		    filename (str): Имя файла.
			save_dir (str): Каталог для сохранения файлов
		"""
		if not os.path.exists(save_dir):
			os.makedirs(save_dir)
		fn = os.path.join(save_dir, filename)
		if not os.path.exists(fn):
			with open(fn, 'w', encoding='utf-8') as f:
				json.dump(SETTINGS, f, indent = 2, ensure_ascii=False)
			self.__data = SETTINGS
		else:
			with open(fn, 'r', encoding='utf-8') as f:
				self.__data = json.loads(f.read())

	def __getitem__(self, item: str) -> dict:
		"""Возвращает фрагмент словаря настроек."""
		return self.__data[item]