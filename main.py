import warnings
from src.app_window import App

BASE_DIR = 'app_data'
"""Каталог для сохранения файлов settings.json и error.txt.""" 

if __name__ == '__main__':
	warnings.filterwarnings('ignore')
	app = App(BASE_DIR)
	app.mainloop()