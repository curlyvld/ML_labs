import sqlite3
import numpy as np
from datetime import datetime


# Класс для работы с SQLite базой данных
class FireSuppressionDB:
    def __init__(self, db_path="fire_suppression.db"):
        """Инициализация SQLite базы данных"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.initialize_database()
        self.populate_rules()
        print("SQLite база данных инициализирована")
    
    def initialize_database(self):
        """Создание таблиц в базе данных"""
        cursor = self.conn.cursor()
        
        # Таблица для хранения правил
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smoke_level TEXT NOT NULL,
                zone_type TEXT NOT NULL,
                action_name TEXT NOT NULL,
                action_description TEXT NOT NULL,
                priority INTEGER NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def populate_rules(self):
        """Заполнение таблицы правил для системы пожаротушения"""
        cursor = self.conn.cursor()
        
        # Проверяем, есть ли уже правила
        cursor.execute("SELECT COUNT(*) FROM rules")
        if cursor.fetchone()[0] > 0:
            return
        
        rules = [
            # Нет дыма
            ("None", "Safe", "Monitor", "Система в режиме мониторинга", 1),
            ("None", "Warning", "PreventiveCheck", "Профилактическая проверка", 2),
            ("None", "Danger", "InspectZone", "Инспекция опасной зоны", 3),
            
            # Небольшой дым
            ("Low", "Safe", "Alert", "Звуковое оповещение", 2),
            ("Low", "Warning", "AlertAndVentilate", "Оповещение и включение вентиляции", 3),
            ("Low", "Danger", "ActivateSprinklersLocal", "Активация локальных спринклеров", 4),
            
            # Сильное задымление
            ("High", "Safe", "EvacuateAndVentilate", "Эвакуация и принудительная вентиляция", 5),
            ("High", "Warning", "FullEvacuation", "Полная эвакуация здания", 6),
            ("High", "Warning", "CriticalEvacuation", "Критическая эвакуация с полной активацией спринклеров", 8),
            ("High", "Danger", "EmergencyProtocol", "Аварийный протокол - полная активация систем", 7),
            ("High", "Danger", "MaximumResponse", "Максимальный отклик - все системы активны", 9),
            ("High", "Danger", "FireEmergency", "ПОЖАР! Все системы активны, вызов пожарных", 10),
        ]
        
        cursor.executemany('''
            INSERT INTO rules (smoke_level, zone_type, action_name, action_description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', rules)
        
        self.conn.commit()
        print("Правила загружены в SQLite")
    
    def get_action(self, smoke_condition, zone_condition):
        """Получение действия из правил SQLite"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT action_name, action_description, priority
            FROM rules
            WHERE smoke_level = ? AND zone_type = ?
            ORDER BY priority DESC
            LIMIT 1
        ''', (smoke_condition, zone_condition))
        
        result = cursor.fetchone()
        if result:
            return result
        return ("NoAction", "Нет подходящего действия", 0)
    
    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()


# Класс для управления системой пожаротушения в здании
class FireSuppressionSystem:
    def __init__(self, db_path="fire_suppression.db"):
        """
        Инициализация системы пожаротушения
        
        Args:
            db_path: путь к файлу SQLite базы данных
        """
        self.db = FireSuppressionDB(db_path)
        print("Система пожаротушения инициализирована")
        print("=" * 70)

    def close(self):
        """Закрытие соединения с базой данных"""
        self.db.close()
        print("\n" + "=" * 70)
        print("Соединение с базой данных закрыто")

    def get_action(self, smoke_level, temperature, zone_risk):
        """
        Получение действия на основе текущих условий
        
        Args:
            smoke_level: уровень дыма (ppm)
            temperature: температура (°C)
            zone_risk: оценка риска зоны (0-100)
            
        Returns:
            tuple: (название действия, описание, приоритет)
        """
        # Фаззификация (преобразование числовых значений в категории)
        smoke_condition = self.fuzzify_smoke(smoke_level)
        zone_condition = self.fuzzify_zone(zone_risk)

        # Получение действия из SQLite
        return self.db.get_action(smoke_condition, zone_condition)

    def fuzzify_smoke(self, smoke_level):
        """
        Фаззификация уровня дыма
        
        Args:
            smoke_level: концентрация дыма в ppm
            
        Returns:
            str: "None", "Low", "High"
        """
        if smoke_level >= 50:
            return "High"  # Сильное задымление
        elif smoke_level >= 10:
            return "Low"  # Небольшое количество дыма
        else:
            return "None"  # Дыма нет

    def fuzzify_temperature(self, temperature):
        """
        Фаззификация температуры
        
        Args:
            temperature: температура в °C
            
        Returns:
            str: "Normal", "Elevated", "Critical"
        """
        if temperature >= 70:
            return "Critical"  # Критическая температура
        elif temperature >= 40:
            return "Elevated"  # Повышенная температура
        else:
            return "Normal"  # Нормальная температура

    def fuzzify_zone(self, zone_risk):
        """
        Фаззификация уровня риска зоны
        
        Args:
            zone_risk: оценка риска зоны (0-100)
            
        Returns:
            str: "Safe", "Warning", "Danger"
        """
        if zone_risk >= 70:
            return "Danger"  # Опасная зона
        elif zone_risk >= 40:
            return "Warning"  # Зона предупреждения
        else:
            return "Safe"  # Безопасная зона

    def display_status(self, step, smoke, temp, zone_risk, action, description, priority):
        """Отображение текущего статуса системы"""
        smoke_cat = self.fuzzify_smoke(smoke)
        temp_cat = self.fuzzify_temperature(temp)
        zone_cat = self.fuzzify_zone(zone_risk)
        
        print(f"\nШаг {step}:")
        print(f"   Дым: {smoke:.1f} ppm [{smoke_cat}]")
        print(f"   Температура: {temp:.1f}°C [{temp_cat}]")
        print(f"   Риск зоны: {zone_risk:.1f}% [{zone_cat}]")
        print(f"   Действие: {action} (приоритет: {priority})")
        print(f"   {description}")

    def simulate(self, initial_smoke, initial_temp, initial_zone_risk, steps=15):
        """
        Симуляция работы системы пожаротушения
        
        Args:
            initial_smoke: начальный уровень дыма (ppm)
            initial_temp: начальная температура (°C)
            initial_zone_risk: начальный риск зоны (0-100)
            steps: количество шагов симуляции
        """
        smoke = initial_smoke
        temp = initial_temp
        zone_risk = initial_zone_risk

        print(f"\nЗапуск симуляции системы пожаротушения")
        print(f"   Начальные условия: Дым={smoke} ppm, Температура={temp}°C, Риск зоны={zone_risk}%")
        print("=" * 70)

        for step in range(steps):
            # Получаем действие на основе текущих условий
            action, description, priority = self.get_action(smoke, temp, zone_risk)
            
            # Отображаем текущее состояние
            self.display_status(step, smoke, temp, zone_risk, action, description, priority)

            # Изменение условий на основе предпринятых действий
            if "Sprinklers" in action or "Emergency" in action or "Maximum" in action:
                # Активация спринклеров снижает температуру и дым
                temp -= np.random.uniform(5, 15)
                smoke -= np.random.uniform(10, 25)
                zone_risk -= np.random.uniform(10, 20)
                
            elif "Evacuate" in action or "Evacuation" in action:
                # Эвакуация снижает риск для людей, но условия могут ухудшаться
                zone_risk -= np.random.uniform(15, 25)
                temp += np.random.uniform(2, 8)
                smoke += np.random.uniform(3, 10)
                
            elif "Ventilate" in action:
                # Вентиляция снижает дым
                smoke -= np.random.uniform(5, 15)
                temp -= np.random.uniform(2, 5)
                zone_risk -= np.random.uniform(5, 10)
                
            elif "Alert" in action:
                # Оповещение - условия изменяются естественным образом
                temp += np.random.uniform(1, 5)
                smoke += np.random.uniform(2, 8)
                zone_risk += np.random.uniform(2, 8)
                
            elif action == "Monitor":
                # Режим мониторинга - небольшие случайные изменения
                temp += np.random.uniform(-1, 2)
                smoke += np.random.uniform(-1, 3)
                zone_risk += np.random.uniform(-2, 5)
            else:
                # Для остальных действий - умеренное изменение
                temp += np.random.uniform(-3, 5)
                smoke += np.random.uniform(-3, 7)
                zone_risk += np.random.uniform(-5, 10)

            # Ограничиваем значения в разумных пределах
            smoke = max(0, min(100, smoke))
            temp = max(15, min(150, temp))
            zone_risk = max(0, min(100, zone_risk))

            # Округляем значения
            smoke = round(smoke, 1)
            temp = round(temp, 1)
            zone_risk = round(zone_risk, 1)

            # Проверка критических условий
            if temp >= 100 and smoke >= 70:
                print("\n" + "=" * 35)
                print("КРИТИЧЕСКАЯ СИТУАЦИЯ! Пожар вышел из-под контроля!")
                print("=" * 35)
                break
            
            # Проверка на успешное тушение
            if smoke < 5 and temp < 30 and zone_risk < 20:
                print("\n" + "=" * 35)
                print("УСПЕХ! Пожар локализован и потушен!")
                print("=" * 35)
                break


# Запуск симуляции
if __name__ == "__main__":
    # Инициализация системы пожаротушения (используется SQLite)
    system = FireSuppressionSystem("fire_suppression.db")

    try:
        # СЦЕНАРИЙ 1: Небольшое возгорание
        print("\n" + "=" * 70)
        print("СЦЕНАРИЙ 1: Небольшое возгорание в безопасной зоне")
        print("=" * 70)
        system.simulate(
            initial_smoke=15,      # Небольшое количество дыма
            initial_temp=35,        # Слегка повышенная температура
            initial_zone_risk=25,   # Низкий риск зоны
            steps=12
        )

        # СЦЕНАРИЙ 2: Серьезный пожар
        print("\n\n" + "=" * 70)
        print("СЦЕНАРИЙ 2: Серьезный пожар в опасной зоне")
        print("=" * 70)
        system.simulate(
            initial_smoke=55,       # Сильное задымление
            initial_temp=65,        # Высокая температура
            initial_zone_risk=75,   # Высокий риск зоны
            steps=15
        )

        # СЦЕНАРИЙ 3: Критическая ситуация
        print("\n\n" + "=" * 70)
        print("СЦЕНАРИЙ 3: Критическая ситуация")
        print("=" * 70)
        system.simulate(
            initial_smoke=70,       # Очень сильное задымление
            initial_temp=80,        # Критическая температура
            initial_zone_risk=85,   # Критический риск
            steps=10
        )

    finally:
        # Закрытие соединения с базой данных
        system.close()
