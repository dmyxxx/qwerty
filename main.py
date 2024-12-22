from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
import sys
import pymysql
from db_config import db_config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Автовокзал - Подсчеты")
        self.setGeometry(100, 100, 400, 300)

        # Подключение к базе данных
        self.connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()

        # Кнопки
        self.btn_count_routes = QPushButton("Подсчет рейсов по станциям")
        self.btn_count_passengers = QPushButton("Подсчет общего количества пассажиров")

        # Подключение кнопок к методам
        self.btn_count_routes.clicked.connect(self.count_routes)
        self.btn_count_passengers.clicked.connect(self.count_passengers)

        # Добавление кнопок в layout
        layout.addWidget(self.btn_count_routes)
        layout.addWidget(self.btn_count_passengers)

        central_widget.setLayout(layout)

    def count_routes(self):
        # Подсчет количества рейсов по станциям
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT stations.name AS station, COUNT(routes.id) AS num_routes
            FROM stations
            LEFT JOIN routes ON stations.id = routes.station_id
            GROUP BY stations.id;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        # Формирование сообщения
        message = "\n".join(f"{row['station']}: {row['num_routes']} рейсов" for row in results)
        QMessageBox.information(self, "Результат подсчета рейсов", message)

    def count_passengers(self):
        # Подсчет общего количества пассажиров
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT SUM(buses.capacity) AS total_capacity
            FROM routes
            JOIN buses ON routes.bus_id = buses.id;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()

        total_capacity = result['total_capacity'] or 0
        QMessageBox.information(self, "Общее количество пассажиров", f"Всего пассажиров: {total_capacity}")

    def closeEvent(self, event):
        # Закрытие подключения к базе данных
        try:
            if self.connection and self.connection.open:
                self.connection.close()
        except Exception as e:
            print(f"Ошибка при закрытии подключения: {e}")
        event.accept()


# Основной запуск приложения
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
