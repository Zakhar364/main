import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox)
from PIL import Image, ImageSequence
import os

# --- Расширенные Ядра функций конвертации ---

# Поддерживаемые форматы (для справки: PIL поддерживает их все для чтения и записи)
SUPPORTED_EXTENSIONS = {
    'JPG': '.jpg', 'JPEG': '.jpg', 
    'PNG': '.png', 
    'GIF': '.gif',
    'TIFF': '.tiff', 'TIF': '.tif',
    'BMP': '.bmp',
    'WEBP': '.webp'
}

def convert_jpg_to_png_core(input_path, output_path=None):
    """Конвертирует JPG в PNG."""
    try:
        img = Image.open(input_path)
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + ".png"
        img.save(output_path, "PNG")
        return True, f"✅ JPG -> PNG успешно: {output_path}"
    except Exception as e:
        return False, f"❌ Ошибка при конвертации JPG в PNG: {e}"

def convert_image_to_format_core(input_path, target_format, output_path=None, quality=95):
    """Универсальная функция для конвертации любого формата в другой (с опцией качества)."""
    try:
        img = Image.open(input_path)
        
        # Получаем расширение для сохранения
        ext = SUPPORTED_EXTENSIONS.get(target_format.upper(), f".{target_format.lower()}")
        
        if output_path is None:
            # Имя файла без расширения + новое расширение
            output_path = os.path.splitext(input_path)[0] + ext
            
        save_params = {}
        fmt = target_format.upper()
        # PIL ожидает 'JPEG', а не 'JPG'
        if fmt == "JPG":
            fmt = "JPEG"
        if fmt == "JPEG":
            save_params['quality'] = quality
            # JPEG не поддерживает альфа-канал
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
        
        if fmt == "GIF":
            # Обработка анимированных GIF
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
            if len(frames) == 1:
                frames[0].save(output_path, format="GIF")
            else:
                frames[0].save(output_path, format="GIF", save_all=True, append_images=frames[1:], loop=0)
        else:
            img.save(output_path, format=fmt, **save_params)

        return True, f"✅ {os.path.basename(input_path)} -> {fmt} успешно: {output_path}"
    except Exception as e:
        return False, f"❌ Ошибка при конвертации в {target_format}: {e}"


# --- Класс GUI на PyQt5 ---
class ImageConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Converter (JPG, PNG, GIF, TIFF, BMP, WEBP)")
        
        # Увеличиваем ширину окна до 1000px
        self.setGeometry(100, 100, 1000, 200) 
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 1. Поле ввода пути
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText("Укажите путь к файлу...")
        
        path_layout = QHBoxLayout()
        
        path_layout.addWidget(QLabel("Путь к файлу:"))
        
        # Поле ввода растягивается сильнее (Вес 3)
        path_layout.addWidget(self.path_input)
        path_layout.setStretchFactor(self.path_input, 3)
        
        # Кнопка выбора файла
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_file)
        path_layout.addWidget(self.browse_button)
        path_layout.setStretchFactor(self.browse_button, 1)
        
        layout.addLayout(path_layout)

        # 2. Кнопки конвертации
        button_layout = QHBoxLayout()
        
        # Создаем кнопки для всех новых форматов
        formats_to_add = ['PNG', 'JPG', 'GIF', 'TIFF', 'BMP', 'WEBP']
        
        for fmt in formats_to_add:
            btn = QPushButton(f"Конвертировать в {fmt}")
            # Используем лямбду для передачи целевого формата
            btn.clicked.connect(lambda checked, target=fmt: self.convert_file(target))
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Устанавливаем минимальный размер, чтобы компоновщик принял большую ширину
        self.setMinimumSize(1000, 200) 
        self.adjustSize() 

    def browse_file(self):
        # Фильтр для всех поддерживаемых форматов
        filter_string = "Image Files (*.jpg *.jpeg *.png *.gif *.tiff *.tif *.bmp *.webp)"
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", filter_string)
        if file_name:
            self.path_input.setText(file_name)

    def convert_file(self, target_format):
        input_path = self.path_input.text()

        if not os.path.exists(input_path):
            QMessageBox.critical(self, "Ошибка", f"Файл не найден по пути:\n{input_path}")
            return

        # Определяем, откуда конвертируем, чтобы не переконвертировать в тот же формат
        input_ext = os.path.splitext(input_path)[1].lower()
        target_ext = SUPPORTED_EXTENSIONS.get(target_format.upper(), f".{target_format.lower()}")
        
        if input_ext == target_ext:
            QMessageBox.warning(self, "Предупреждение", f"Файл уже имеет формат {target_format.upper()}. Конвертация не требуется.")
            return

        # Вызываем универсальное ядро
        success, message = convert_image_to_format_core(input_path, target_format)
        
        # Вывод результата во всплывающем окне
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)


if __name__ == '__main__':
    # Инициализация PyQt5
    app = QApplication(sys.argv)
    ex = ImageConverterApp()
    ex.show()
    sys.exit(app.exec())
