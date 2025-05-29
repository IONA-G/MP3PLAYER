# Импорт необходимых библиотек
import tkinter as tk  # Для создания графического интерфейса
from tkinter import filedialog  # Для диалогового окна выбора файлов
from pygame import mixer  # Для воспроизведения аудиофайлов
from PIL import Image, ImageTk  # Для работы с изображениями 
import os  # Для работы с путями к файлам

# Проверяем доступность библиотеки PIL (Pillow)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True  # Флаг доступности PIL
except ImportError:
    PIL_AVAILABLE = False  # Если библиотека не установлена
    print("Библиотека Pillow не установлена.")

class MP3Player:
    def __init__(self, root):
        """Инициализация основного окна приложения"""
        self.root = root 
        self.root.title("Python MP3 Player")  # Устанавливаем заголовок окна
        self.root.geometry("400x200")  # Устанавливаем размеры окна
        self.root.resizable(False, False)  # Запрет изменения размеров
        
        # Настройка фона приложения
        self.setup_background()
        
        # Инициализация аудио-микшера pygame
        mixer.init()
        
        # Создание переменных для хранения состояния плеера
        self.current_track = tk.StringVar()  # Хранит название текущего трека
        self.track_length = 0  # Длина трека в секундах
        self.playing_state = False  # Флаг состояния воспроизведения (True/False)
        self.volume_level = tk.DoubleVar()  # Уровень громкости (0.0-1.0)
        self.volume_level.set(0.7)  # Установка громкости по умолчанию на 70%
        
        # Создание элементов интерфейса
        self.create_widgets()
    
    def setup_background(self):
        """Настройка фона приложения"""
        if PIL_AVAILABLE:
            try:
                # Загружаем фон 
                bg_image = Image.open(r"C:\Users\lxndr\OneDrive\Рабочий стол\ВВедение в проф деятельность\Fon.jpg")  # Используем относительный путь
                bg_image = bg_image.resize((400, 200), Image.LANCZOS)  # Масштабируем под размер окна
                self.bg_image = ImageTk.PhotoImage(bg_image)  # Создаем объект изображения для Tkinter
                
                # Создаем метку с фоновым изображением
                bg_label = tk.Label(self.root, image=self.bg_image)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Растягиваем на все окно
            except Exception as e:
                print(f"Ошибка загрузки фона: {e}")
                # Если фон не выбран то будет простая заливка 
                self.root.configure(bg="#336652")
        else:
            # Если PIL не работает, используем цветной фон
            self.root.configure(bg='#2c3e50')
    
    def create_widgets(self):
        """Создание всех элементов графического интерфейса"""
        # Фрейм для кнопок управления (контейнер)
        control_frame = tk.Frame(self.root, bg="#052f58")  # Цвет фона как у основного
        control_frame.pack(pady=10)  # Размещаем с отступом 10 пикселей сверху и снизу
        
        # Создаем кнопки управления
        # Кнопка выбора трека
        btn_load = tk.Button(
            control_frame, 
            text="Выбрать трек", 
            command=self.load_track,
            bg='#3498db',  # Цвет кнопки
            fg='white'     # Цвет текста
        )
        
        # Кнопка воспроизведения/паузы
        btn_play = tk.Button(
            control_frame, 
            text="▶", 
            command=self.play_pause, 
            width=5,
            bg='#2ecc71',  # Зеленый цвет для кнопки play
            fg='white'
        )
        
        # Кнопка перемотки назад (-10 секунд)
        btn_rewind_back = tk.Button(
            control_frame, 
            text="<<", 
            command=lambda: self.rewind(-10),
            bg='#34495e',  # Темный цвет
            fg='white'
        )
        
        # Кнопка перемотки вперед (+10 секунд)
        btn_rewind_forward = tk.Button(
            control_frame, 
            text=">>", 
            command=lambda: self.rewind(10),
            bg='#34495e',  # Темный цвет
            fg='white'
        )
        
        # Размещаем кнопки в сетке (grid)
        btn_load.grid(row=0, column=0, padx=5)
        btn_rewind_back.grid(row=0, column=1, padx=5)
        btn_play.grid(row=0, column=2, padx=5)
        btn_rewind_forward.grid(row=0, column=3, padx=5)
        
        # Метка для ползунка громкости
        volume_label = tk.Label(
            self.root, 
            text="Громкость:",
            bg='#2c3e50',  # Цвет фона как у основного
            fg='white'     # Белый текст
        )
        volume_label.pack()
        
        # Ползунок громкости
        volume_slider = tk.Scale(
            self.root, 
            from_=0, to=1,  # Диапазон значений громкости
            resolution=0.01,  # Шаг изменения (1%)
            orient=tk.HORIZONTAL,  # Горизонтальная ориентация
            variable=self.volume_level,  # Привязка к переменной громкости
            command=self.set_volume,  # Обработчик изменения громкости
            bg='#2c3e50',  # Цвет фона
            fg='white',    # Цвет текста
            highlightthickness=0  # Убираем выделение
        )
        volume_slider.pack(fill=tk.X, padx=20)  # Растягиваем по ширине с отступами
        
        # Метка для отображения названия текущего трека
        track_label = tk.Label(
            self.root, 
            textvariable=self.current_track,  # Привязка к переменной с названием трека
            wraplength=380,  # Максимальная ширина текста перед переносом
            bg='#2c3e50',    # Цвет фона
            fg='white'       # Цвет текста
        )
        track_label.pack(pady=10)  # Размещаем с отступом
        
        # Ползунок прогресса воспроизведения
        self.progress_slider = tk.Scale(
            self.root, 
            from_=0, to=100,  # Диапазон значений (в процентах)
            orient=tk.HORIZONTAL,  # Горизонтальная ориентация
            command=self.on_progress_change,  # Обработчик изменения позиции
            bg='#2c3e50',  # Цвет фона
            fg='white',    # Цвет текста
            highlightthickness=0  # Убираем выделение
        )
        self.progress_slider.pack(fill=tk.X, padx=20, pady=5)  # Растягиваем по ширине
        
        # Запускаем обновление прогресса воспроизведения
        self.update_progress()
    
    def load_track(self):
        """Загрузка аудиофайла"""
        # Открываем диалоговое окно выбора файла (только MP3)
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        
        if file_path:  # Если файл выбран
            # Устанавливаем название файла (без пути)
            self.current_track.set(os.path.basename(file_path))
            
            # Загружаем трек в микшер pygame
            mixer.music.load(file_path)
            
            # Получаем длительность трека в секундах
            self.track_length = mixer.Sound(file_path).get_length()
            
            # Устанавливаем максимальное значение для ползунка прогресса
            self.progress_slider.config(to=self.track_length)
            
            # Автоматически начинаем воспроизведение
            self.play_pause()
    
    def play_pause(self):
        """Управление воспроизведением/паузой"""
        if self.current_track.get():  # Если трек выбран
            if not self.playing_state:  # Если не воспроизводится
                mixer.music.play()  # Начинаем воспроизведение
                self.playing_state = True  # Устанавливаем флаг воспроизведения
            else:
                mixer.music.pause()  # Ставим на паузу
                self.playing_state = False  # Снимаем флаг воспроизведения
    
    def rewind(self, seconds):
        """Перемотка трека вперед/назад"""
        if self.current_track.get():  # Если трек выбран
            # Получаем текущую позицию в секундах
            current_pos = mixer.music.get_pos() / 1000  
            
            # Вычисляем новую позицию (не меньше 0)
            new_pos = max(0, current_pos + seconds)  
            
            # Устанавливаем новую позицию воспроизведения
            mixer.music.set_pos(new_pos)  
    
    def set_volume(self, val):
        """Установка громкости"""
        mixer.music.set_volume(float(val))  # Устанавливаем уровень громкости (0.0-1.0)
    
    def on_progress_change(self, value):
        """Обработка изменения позиции через ползунок"""
        if self.current_track.get():  # Если трек выбран
            mixer.music.set_pos(float(value))  # Устанавливаем новую позицию
    
    def update_progress(self):
        """Обновление позиции воспроизведения"""
        if self.playing_state and self.current_track.get():  # Если трек воспроизводится
            # Получаем текущую позицию в секундах
            current_pos = mixer.music.get_pos() / 1000  

            # Обновляем положение ползунка
            self.progress_slider.set(current_pos)  
        
        # Повторно вызываем эту функцию через 1 секунду (1000 мс)
        self.root.after(1000, self.update_progress)

if __name__ == "__main__":
    """Точка входа в приложение"""
    root = tk.Tk()  # Создаем главное окно
    app = MP3Player(root)  # Создаем экземпляр плеера
    root.mainloop()  # Запускаем главный цикл обработки событий