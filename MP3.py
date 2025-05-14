# Импорт необходимых библиотек
import tkinter as tk  #Библиотека для графического интерфейса
from tkinter import filedialog  #Библиотека для диалога выбора файлов
from pygame import mixer  # Библиотека для воспроизведения аудио
import os  #Библиотека для работы с путями файлов

class MP3Player:
    def __init__(self, root):
        """Инициализация основного окна приложения"""
        self.root = root
        self.root.title("Python MP3 Player")  # Заголовок окна
        self.root.geometry("400x200")  # Размеры окна
        
        # Инициализация аудио-микшера pygame
        mixer.init()
        
        # Создание переменных для хранения состояния плеера
        self.current_track = tk.StringVar()  # Текущий трек
        self.track_length = 0  # Длина трека в секундах
        self.playing_state = False  # Состояние воспроизведения (True/False)
        self.volume_level = tk.DoubleVar()  # Уровень громкости (0.0-1.0)
        self.volume_level.set(0.7)  # Установка громкости по умолчанию на 70%
        
        # Создание элементов интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        """Создание всех элементов графического интерфейса"""
        # Фрейм для кнопок управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)  # Размещение с отступом
        
        # Создание кнопок:
        # Кнопка выбора трека
        btn_load = tk.Button(control_frame, text="Выбрать трек", command=self.load_track)
        # Кнопка воспроизведения/паузы
        btn_play = tk.Button(control_frame, text="▶", command=self.play_pause, width=5)
        # Кнопка перемотки назад
        btn_rewind_back = tk.Button(control_frame, text="<<", command=lambda: self.rewind(-10))
        # Кнопка перемотки вперед
        btn_rewind_forward = tk.Button(control_frame, text=">>", command=lambda: self.rewind(10))
        
        # Размещение кнопок в сетке
        btn_load.grid(row=0, column=0, padx=5)
        btn_rewind_back.grid(row=0, column=1, padx=5)
        btn_play.grid(row=0, column=2, padx=5)
        btn_rewind_forward.grid(row=0, column=3, padx=5)
        
        # Метка для ползунка громкости
        volume_label = tk.Label(self.root, text="Громкость:")
        volume_label.pack()
        
        # Ползунок громкости
        volume_slider = tk.Scale(
            self.root, 
            from_=0, to=1,  # Диапазон значений
            resolution=0.01,  # Шаг изменения
            orient=tk.HORIZONTAL,  # Горизонтальная ориентация
            variable=self.volume_level,  # Привязка к переменной
            command=self.set_volume  # Обработчик изменения
        )
        volume_slider.pack(fill=tk.X, padx=20)  # Размещение с заполнением по ширине
        
        # Метка для отображения названия текущего трека
        track_label = tk.Label(
            self.root, 
            textvariable=self.current_track,  # Привязка к переменной
            wraplength=380  # Максимальная ширина текста
        )
        track_label.pack(pady=10)  # Размещение с отступом
        
        # Ползунок прогресса воспроизведения
        self.progress_slider = tk.Scale(
            self.root, 
            from_=0, to=100,  # Диапазон значений
            orient=tk.HORIZONTAL,  # Горизонтальная ориентация
            command=self.on_progress_change  # Обработчик изменения
        )
        self.progress_slider.pack(fill=tk.X, padx=20, pady=5)  # Размещение
        
        # Запуск обновления прогресса воспроизведения
        self.update_progress()
    
    def load_track(self):
        """Загрузка аудиофайла"""
        # Открытие диалога выбора файла
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            # Установка названия файла
            self.current_track.set(os.path.basename(file_path))
            # Загрузка трека в микшер
            mixer.music.load(file_path)
            # Получение длительности трека
            self.track_length = mixer.Sound(file_path).get_length()
            # Установка максимального значения для ползунка прогресса
            self.progress_slider.config(to=self.track_length)
            # Автоматическое начало воспроизведения
            self.play_pause()
    
    def play_pause(self):
        """Управление воспроизведением/паузой"""
        if self.current_track.get():  # Если трек выбран
            if not self.playing_state:  # Если не воспроизводится
                mixer.music.play()  # Начать воспроизведение
                self.playing_state = True  # Установить флаг
            else:
                mixer.music.pause()  # Поставить на паузу
                self.playing_state = False  # Снять флаг
    
    def rewind(self, seconds):
        """Перемотка трека"""
        if self.current_track.get():  # Если трек выбран
            current_pos = mixer.music.get_pos() / 1000  # Текущая позиция в секундах
            new_pos = max(0, current_pos + seconds)  # Новая позиция
            mixer.music.set_pos(new_pos)  # Установка позиции
    
    def set_volume(self, val):
        """Установка громкости"""
        mixer.music.set_volume(float(val))  # Установка уровня громкости
    
    def on_progress_change(self, value):
        """Обработка изменения позиции через ползунок"""
        if self.current_track.get():  # Если трек выбран
            mixer.music.set_pos(float(value))  # Установка новой позиции
    
    def update_progress(self):
        """Обновление позиции воспроизведения"""
        if self.playing_state and self.current_track.get():  # Если трек воспроизводится
            current_pos = mixer.music.get_pos() / 1000  # Текущая позиция в секундах
            self.progress_slider.set(current_pos)  # Обновление ползунка
        # Повторный вызов через 1 секунду
        self.root.after(1000, self.update_progress)

if __name__ == "__main__":
    """Точка входа в приложение"""
    root = tk.Tk()  # Создание главного окна
    app = MP3Player(root)  # Создание экземпляра плеера
    root.mainloop()  # Запуск основного цикла обработки событий