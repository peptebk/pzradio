# -*- coding: utf-8 -*-
"""
Современный плоский интерфейс для интернет-радиоплеера
Windows 10 стиль, PyQt5
Оболочка для модулей: stations.py и radio.py
"""

import sys
import threading
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QSlider,
    QLabel, QDialog, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon

import stations
from radio import Radio
from record import Recorder

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

# Цвета интерфейса
COLOR_BG_LIGHT = "#F0F0F0"
COLOR_PANEL = "#FFFFFF"
COLOR_BORDER = "#D0D0D0"
COLOR_ACTIVE = "#494846"
COLOR_ACTIVE_LIGHT = "#E8F4F8"
COLOR_TEXT_DARK = "#333333"
COLOR_TEXT_LIGHT = "#666666"
COLOR_BUTTON_HOVER = "#E1E1E1"

COLOR_BG = "#494846"
COLOR_HOVER = "#52504e"
COLOR_PRESSED = "#63625f"

class AddStationDialog(QDialog):
    """Диалоговое окно для добавления новой радиостанции"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить станцию")
        self.setModal(True)
        self.setStyleSheet(self._get_stylesheet())
        self.init_ui()
        self.station_data = None

    def init_ui(self):
        """Инициализирует UI диалога"""
        layout = QVBoxLayout()
        name_label = QLabel("Название станции:")
        name_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Радиостанция FM")
        self.name_input.setFont(QFont("Segoe UI", 10))
        self.name_input.setMinimumHeight(35)
        layout.addWidget(self.name_input)
        url_label = QLabel("URL радиопотока:")
        url_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Например: https://example.com/stream.mp3")
        self.url_input.setFont(QFont("Segoe UI", 10))
        self.url_input.setMinimumHeight(35)
        layout.addWidget(self.url_input)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        ok_button = QPushButton("Добавить")
        ok_button.setFont(QFont("Segoe UI", 10))
        ok_button.setMinimumWidth(100)
        ok_button.setMinimumHeight(35)
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.setFont(QFont("Segoe UI", 10))
        cancel_button.setMinimumWidth(100)
        cancel_button.setMinimumHeight(35)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addSpacing(20)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setMinimumWidth(450)

    def accept(self):
        """Подтверждение добавления"""
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название станции")
            return

        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL потока")
            return

        self.station_data = {"name": name, "url": url}
        super().accept()

    def _get_stylesheet(self):
        """Возвращает стили для диалога"""
        return f"""
            QDialog {{
                background-color: {COLOR_PANEL};
            }}
            QLineEdit {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 5px;
                background-color: #FAFAFA;
                color: {COLOR_TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_ACTIVE};
            }}
            QPushButton {{
                background-color: {COLOR_ACTIVE};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1084D7;
            }}
        """


class RadioPlayer(QMainWindow):
    """Главное окно приложения радиоплеера"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pz-radio")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon('icon.png')) 

        self.radio = Radio()
        self.recorder = Recorder()
        self.current_station_index = None
        self.is_playing = False
        self.is_recording = False
        
        self.init_ui()
        self.apply_styles()
        self.update_stations_list()
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    def init_ui(self):
        """Инициализирует главный интерфейс"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)

        center_panel = self.create_center_panel()
        content_layout.addWidget(center_panel, 2)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)

    def create_top_panel(self):
        """Создает верхнюю панель с кнопками управления"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLOR_PANEL}; border-bottom: 1px solid {COLOR_BORDER};")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        add_btn = QPushButton("Добавить")
        add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        add_btn.setMinimumHeight(35)
        add_btn.setMinimumWidth(120)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRESSED};
            }}
        """)
        add_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        add_btn.clicked.connect(self.add_station)
        layout.addWidget(add_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        delete_btn.setMinimumHeight(35)
        delete_btn.setMinimumWidth(120)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRESSED};
            }}
        """)
        delete_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        delete_btn.clicked.connect(self.delete_station)
        layout.addWidget(delete_btn)

        layout.addStretch()

        return panel

    def create_left_panel(self):
        """Создает левую боковую панель со списком станций"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLOR_BG_LIGHT}; border-right: 1px solid {COLOR_BORDER};")
        panel.setMinimumWidth(250)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("📻 Станции")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet(f"padding: 10px; background-color: {COLOR_PANEL}; border-bottom: 1px solid {COLOR_BORDER};")
        layout.addWidget(title)

        self.stations_list = QListWidget()
        self.stations_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: {COLOR_BG_LIGHT};
            }}
            QListWidget::item {{
                padding: 10px;
                margin: 2px 4px;
                border-radius: 4px;
                background-color: {COLOR_PANEL};
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_PANEL};
                border-left: 3px solid {COLOR_ACTIVE};
                color: {COLOR_TEXT_DARK};
            }}
            QListWidget::item:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            /* Scrollbar styling to match app style */
            QListWidget QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 12px 0 12px 0;
            }}
            QListWidget QScrollBar::handle:vertical {{
                background: {COLOR_BG};
                min-height: 30px;
                border-radius: 6px;
            }}
            QListWidget QScrollBar::handle:vertical:hover {{
                background: {COLOR_HOVER};
            }}
            QListWidget QScrollBar::add-line, QListWidget QScrollBar::sub-line {{
                height: 0px;
                background: none;
                border: none;
            }}
        """)
        self.stations_list.itemClicked.connect(self.on_station_selected)
        layout.addWidget(self.stations_list)

        return panel

    def create_center_panel(self):
        """Создает центральную область с информацией о станции"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLOR_PANEL};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(30, 30, 30, 30)

        layout.addStretch()

        self.current_station_label = QLabel("Выберите станцию")
        self.current_station_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.current_station_label.setStyleSheet(f"color: {COLOR_TEXT_DARK}; background-color: transparent;")
        self.current_station_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_station_label)

        layout.addSpacing(20)

        self.status_label = QLabel("Остановлено")
        self.status_label.setFont(QFont("Segoe UI", 16))
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_LIGHT}; background-color: transparent;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        return panel

    def create_bottom_panel(self):
        """Создает нижнюю панель с регулятором громкости и кнопкой управления"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLOR_PANEL}; border-top: 1px solid {COLOR_BORDER};")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMinimumWidth(200)
        self.volume_slider.setStyleSheet("QSlider { border: none; }")
        self.volume_slider.sliderMoved.connect(self.on_volume_changed)
        layout.addWidget(self.volume_slider)

        self.volume_percent_label = QLabel("50")
        self.volume_percent_label.setFont(QFont("Segoe UI", 10))
        self.volume_percent_label.setMinimumWidth(40)
        self.volume_percent_label.setAlignment(Qt.AlignCenter)
        self.volume_percent_label.setStyleSheet("border: none;")
        layout.addWidget(self.volume_percent_label)

        layout.addSpacing(20)

        self.play_btn = QPushButton("▶ Играть")
        self.play_btn.setObjectName("play_button")
        self.play_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.play_btn.setMinimumHeight(35)
        self.play_btn.setMinimumWidth(130)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRESSED};
            }}
        """)
        self.play_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.play_btn.clicked.connect(self.toggle_playback)
        layout.addWidget(self.play_btn)

        self.record_btn = QPushButton("● Запись")
        self.record_btn.setObjectName("record_button")
        self.record_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.record_btn.setMinimumHeight(35)
        self.record_btn.setMinimumWidth(130)
        self.record_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #8B4545;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #9D5C5C;
            }}
            QPushButton:pressed {{
                background-color: #B87070;
            }}
        """)
        self.record_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)

        layout.addStretch()

        return panel

    def apply_styles(self):
        """Применяет общие стили к приложению"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BG_LIGHT};
            }}
            QPushButton {{
                background-color: {COLOR_ACTIVE};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #1084D7;
            }}
            QPushButton:pressed {{
                background-color: #0063B1;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {COLOR_BORDER};
                height: 6px;
                background: {COLOR_BG_LIGHT};
                border-radius: 1px;
            }}
            QSlider::handle:horizontal {{
                background: {COLOR_BG};
                border: 2px solid {COLOR_BG};
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLOR_BG};
            }}
        """)

    def update_stations_list(self):
        """Обновляет список станций в интерфейсе из stations.py"""
        self.stations_list.clear()
        loaded_stations = stations.load_stations()
        for i, station in enumerate(loaded_stations):
            item = QListWidgetItem(f"▶ {station['name']}")
            item.setFont(QFont("Segoe UI", 10))
            self.stations_list.addItem(item)

    def on_station_selected(self, item):
        """Обработчик выбора станции из списка"""
        index = self.stations_list.row(item)

        if self.is_recording:
            self.recorder.stop_record()
            self.is_recording = False
            self.update_recording_status()

        self.current_station_index = index
        loaded_stations = stations.load_stations()
        if 0 <= index < len(loaded_stations):
            station = loaded_stations[index]
            self.current_station_label.setText(station['name'])

            if self.is_playing:
                self.play_current_station()
                
            self.update_status()

    def add_station(self):
        """Открывает диалог добавления новой станции"""
        dialog = AddStationDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.station_data:
            station = dialog.station_data
            stations.add_station(station['name'], station['url'])
            self.update_stations_list()
            QMessageBox.information(
                self, "pz-radio",
                f"Станция '{station['name']}' успешно добавлена"
            )

    def delete_station(self):
        """Удаляет выбранную станцию"""
        if self.current_station_index is None:
            QMessageBox.warning(self, "pz-radio", "Выберите станцию для удаления")
            return

        loaded_stations = stations.load_stations()
        if self.current_station_index >= len(loaded_stations):
            return

        station_name = loaded_stations[self.current_station_index]['name']
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить станцию '{station_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.is_playing:
                self.stop_playback()

            stations.delete_station(self.current_station_index)
            self.current_station_index = None
            self.current_station_label.setText("Выберите станцию")
            self.update_stations_list()
            QMessageBox.information(self, "pz-radio", f"Станция '{station_name}' удалена")

    def play_current_station(self):
        """Запускает воспроизведение текущей станции"""
        if self.current_station_index is None:

            QMessageBox.warning(self, "pz-radio", "Выберите станцию для воспроизведения")
            return

        loaded_stations = stations.load_stations()
        if self.current_station_index >= len(loaded_stations):
            return

        station = loaded_stations[self.current_station_index]

        def play():
            if self.radio.play(station['url']):
                self.is_playing = True
                self.update_status()
            else:
                QMessageBox.critical(
                    self, "pz-radio",
                    f"Не удалось воспроизвести поток:\n{station['url']}\n\n"
                    "Проверьте URL и интернет-соединение."
                )
                self.is_playing = False
                self.update_status()
        
        thread = threading.Thread(target=play, daemon=True)
        thread.start()

    def stop_playback(self):
        self.radio.stop()
        self.is_playing = False
        self.update_status()

    def toggle_playback(self):
        """Переключает между воспроизведением и остановкой"""
        if self.is_playing:
            self.stop_playback()
        else:
            self.play_current_station()

    def toggle_recording(self):
        """Переключает запись потока"""
        if self.is_recording:
            if self.recorder.stop_record():
                self.is_recording = False
                self.update_recording_status()
        else:
            if self.current_station_index is None:
                QMessageBox.warning(self, "pz-radio", "Выберите станцию для записи")
                return

            loaded_stations = stations.load_stations()
            if self.current_station_index >= len(loaded_stations):
                return

            station = loaded_stations[self.current_station_index]

            def record():
                if self.recorder.start_record(station['url'], station['name']):
                    self.is_recording = True
                    self.update_recording_status()
                else:
                    self.is_recording = False
                    self.update_recording_status()

            thread = threading.Thread(target=record, daemon=True)
            thread.start()

    def update_recording_status(self):
        """Обновляет статус кнопки записи"""
        if self.is_recording:
            self.record_btn.setText("■ Остановить")
        else:
            self.record_btn.setText("● Запись")

    def on_volume_changed(self):
        """Обработчик изменения громкости"""
        volume = self.volume_slider.value()
        self.radio.set_volume(volume)
        self.volume_percent_label.setText(f"{volume}")

    def update_status(self):
        """Обновляет статус воспроизведения"""
        if self.is_playing:
            self.status_label.setText("Воспроизведение")
            self.play_btn.setText("Стоп")
        else:
            self.status_label.setText("Остановлено")
            self.play_btn.setText("▶ Играть")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        if self.is_recording:
            self.recorder.stop_record()
        self.stop_playback()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RadioPlayer()
    window.show()
    sys.exit(app.exec_())
