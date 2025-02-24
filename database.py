import sqlite3
import json

class Database:
    @staticmethod
    def start_database():
        '''
        Инициализирует базу данных и вставляет значения настроек записи по умолчанию, если записей нет.
        '''
        Database.initialize_database()
        return sqlite3.connect('database.db')

    @staticmethod
    def connect_db():
        '''
        Функция для подключения к базе данных.
        '''
        return sqlite3.connect('database.db')

    @staticmethod
    def initialize_database():
        '''
        Инициализирует базу данных, создавая таблицы, если они не существуют.
        '''
        # Открытие соединения и создание таблиц
        with sqlite3.connect('database.db') as conn:
            # Создание таблицы пользователей
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                patronymic TEXT,
                email TEXT UNIQUE,
                birth_date DATE,
                password TEXT
            );
            ''')

            # Создание таблицы миссий
            conn.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                launch_date DATE,
                landing_date DATE,
                launch_site_id INTEGER,
                landing_site_id INTEGER,
                flight_id INTEGER,
                FOREIGN KEY (launch_site_id) REFERENCES launch_sites(id),
                FOREIGN KEY (landing_site_id) REFERENCES landing_sites(id),
                FOREIGN KEY (flight_id) REFERENCES flights(id)
            );
            ''')

            # Создание таблицы космонавтов
            conn.execute('''
            CREATE TABLE IF NOT EXISTS cosmonauts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                birthdate DATE,
                rank TEXT,
                early_life TEXT,
                career TEXT,
                post_flight TEXT
            );
            ''')

            # Создание связующей таблицы экипажа
            conn.execute('''
            CREATE TABLE IF NOT EXISTS crew (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id INTEGER,
                cosmonaut_id INTEGER,
                role TEXT,
                FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
                FOREIGN KEY (cosmonaut_id) REFERENCES cosmonauts(id) ON DELETE CASCADE
            );
            ''')

            # Создание таблицы космических кораблей
            conn.execute('''
            CREATE TABLE IF NOT EXISTS spacecrafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                crew_capacity INTEGER,
                mission_id INT,
                FOREIGN KEY (mission_id) REFERENCES missions(id)
            );
            ''')

            # Создание таблицы космодромов
            conn.execute('''
            CREATE TABLE IF NOT EXISTS launch_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                latitude TEXT,
                longitude TEXT
            );
            ''')

            # Создание таблицы посадочных зон
            conn.execute('''
            CREATE TABLE IF NOT EXISTS landing_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                latitude TEXT,
                longitude TEXT,
                country TEXT
            );
            ''')
            
            # Создание таблицы космических полётов
            conn.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT UNIQUE,
                destination TEXT,
                launch_date DATE,
                seats_available INTEGER,
                flight_duration_hours INT,
                flight_duration_minutes INT,
                parachute_landing BOOL,
                impact_velocity_mps INT
            );
            ''')

        print('Database and tables created successfully!')
        
#region Методы

    @staticmethod
    def connect_db():
        '''
        Функция для подключения к базе данных.
        '''
        return sqlite3.connect('database.db')

    @staticmethod
    def insert_data():
        '''
        Вставка данных в таблицы базы данных.
        '''
        conn = Database.connect_db()
        cursor = conn.cursor()

        # 1. Вставляем данные о миссии
        cursor.execute('''INSERT INTO missions (name, launch_date, landing_date, launch_site_id, landing_site_id, flight_id)
                        VALUES (?, ?, ?, ?, ?, ? )''', 
                        ('Восток 1', '1961-04-12', '1961-04-12', 1, 1, 1))

        # 2. Вставляем данные о космодроме (launch_sites)
        cursor.execute('''INSERT INTO launch_sites (name, latitude, longitude) 
                        VALUES (?, ?, ?)''', 
                        ('Космодром Байконур', '45.9650000', '63.3050000', ))

        cursor.execute('''INSERT INTO landing_sites (name, latitude, longitude, country) 
                        VALUES (?, ?, ?, ?)''', 
                        ('Смеловка', '51.2700000', '45.9970000', 'СССР'))

        # 3. Вставляем данные о космическом корабле (spacecrafts)
        cursor.execute('''INSERT INTO spacecrafts (name, manufacturer, crew_capacity, mission_id) 
                        VALUES (?, ?, ?, ?)''', 
                        ('Восток 3KA', 'OKB-1', 1, 1))

        # 4. Вставляем данные о космонавте (cosmonauts)
        cursor.execute('''INSERT INTO cosmonauts (name, birthdate, rank, early_life, career, post_flight) 
                        VALUES (?, ?, ?, ?, ?, ?)''', 
                        ('Юрий Гагарин', '1934-03-09', 'Старший лейтенант', 
                        'Родился в Клушино, Россия.', 
                        'Отобран в отряд космонавтов в 1960 году...',
                        'Стал международным героем.'))

        # 5. Вставляем данные о полете (flights)
        cursor.execute('''INSERT INTO flights (flight_number, destination, launch_date, seats_available, flight_duration_hours, flight_duration_minutes, parachute_landing, impact_velocity_mps) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                        ('1', 'Восток 1', '1961-04-12', 1, 1, 48, True, 7))

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()


    def register_user(first_name, last_name, patronymic, email, password, birth_date):
        '''
        Регистрирует пользователя в базе данных.
        '''
        conn = Database.connect_db()
        cursor = conn.cursor()
        # Проверка на уникальность email
        cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            return False
        # Вставка нового пользователя
        cursor.execute('''
        INSERT INTO users (first_name, last_name, patronymic, email, password, birth_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, patronymic, email.lower(), password, birth_date))
        conn.commit()
        # Получение данных о созданном пользователе
        cursor.execute('SELECT first_name, last_name, patronymic, email FROM users WHERE email = ?', (email.lower(),))
        user = cursor.fetchone()
        # Закрытие соединения с БД
        conn.close()
        
        return True
    
    def authenticate_user(email, password):
        '''
        Аутентификация пользователя.
        '''
        conn = Database.connect_db()
        cursor = conn.cursor()
        # Проверяем, существует ли пользователь с таким email
        cursor.execute('SELECT id, first_name, last_name, patronymic, password, birth_date FROM users WHERE email = ? AND password = ?', (email.lower(), password,))
        user = cursor.fetchone()
        conn.close()
        if not user:
            return False
        else:
            return {'id' : user[0],
                    'name' : f'{user[2]} {user[1]} {user[3]}',
                    'birth_date' : user[5],
                    'email' : email.lower()
                    }
    @staticmethod
    def get_mission_by_name(mission_name):
        conn = Database.connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
                        SELECT m.id, m.name, m.launch_date, m.landing_date, m.launch_site_id, m.landing_site_id, m.flight_id
                        FROM missions m WHERE name = ?
                        ''', (mission_name,))
        result = cursor.fetchone()
        return{
            'id' : result[0],
            'name' : result[1],
            'launch_date' : result[2],
            'landing_date' : result[3],
            'launch_site_id' : result[4],
            'landing_site_id' : result[5],
            'flight_id': result[6]
        }

    @staticmethod
    def get_launch_site_by_id(id):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM launch_sites WHERE id = ?
                        ''', (id,))
        result = cursor.fetchone()
        return{
                'id' : result[0],
                'name' : result[1],
                'latitude' : result[2],
                'longitude' : result[3]
        }
    @staticmethod
    def get_flight_by_id(id):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM flights WHERE id = ?
                        ''', (id,))
        result = cursor.fetchone()
        return{
            'id':result[0],
            'flight_number':result[1],
            'destination':result[2],
            'launch_date':result[3],
            'seats_available':result[4],
            'flight_duration_hours':result[5],
            'flight_duration_minutes':result[6],
            'parachute_landing':result[7],
            'impact_velocity_mps':result[8],
        }
    @staticmethod
    def get_spacecraft_by_mission_id(mission_id):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM spacecrafts WHERE mission_id = ?
                        ''', (mission_id,))
        result = cursor.fetchone()
        return {
            'id' : result[0],
            'name' : result[1],
            'manufacturer' : result[2],
            'crew_capacity' : result[3],
            'mission_id' : result[4]
        }
    @staticmethod
    def get_landing_site_by_id(id):
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM landing_sites WHERE id = ?
                        ''', (id,))
        result = cursor.fetchone()
        return {
            'id': result[0],
            'name': result[1],
            'latitude': result[2],
            'longitude': result[3],
            'country': result[4]
        }
    @staticmethod
    def get_gagarin_cosmonaut_details():
        conn = Database.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM cosmonauts WHERE id = 1
                        ''')
        result = cursor.fetchone()
        return {
            "name": result[1],
            "birthdate": result[2],
            "rank":result[3],
            "bio":{
                "early_life": result[4],
                "career": result[5],
                "post_flight": result[6]
            }
        }
    @staticmethod
    def get_gagarin_detail():        
        mission = Database.get_mission_by_name('Восток 1')
        launch_site = Database.get_launch_site_by_id(mission['launch_site_id'])
        flight = Database.get_flight_by_id(mission['flight_id'])
        spacecraft = Database.get_spacecraft_by_mission_id(mission['id'])
        landing_site = Database.get_landing_site_by_id(mission['landing_site_id'])
        output = {
            'mission': {
                'name' : mission['name'],
                'launch_details': {
                    'launch_date' : mission['launch_date'],
                    'launch_site' : {
                        'name' : launch_site['name'],
                        'location' : {
                            'latitude' : launch_site['latitude'],
                            'longitude' : launch_site['longitude']
                        }
                    }
                },
                'flight_duration' : {
                    'hours': flight['flight_duration_hours'],
                    'minutes': flight['flight_duration_minutes']
                },
                'spacecraft':{
                    'name': spacecraft['name'],
                    'manufacturer': spacecraft['manufacturer'],
                    'crew_capacity': spacecraft['crew_capacity']
                }
            },
            "landing": {
                "date": mission['landing_date'],
                "site": {
                    "name": landing_site['name'],
                    "country": landing_site['country'],
                    "coordinates":{
                        "latitude": landing_site['latitude'],
                        "longitude": landing_site['longitude']
                    }
                },
                "details": {
                    "parachute_landing": flight['parachute_landing'],
                    "impact_velocity_mps": flight['impact_velocity_mps'],
                }
            },
            "cosmonaut":Database.get_gagarin_cosmonaut_details()
        }
        return output
    @staticmethod
    def get_gagarin_mission():
        output = {
            'data' : [
                Database.get_gagarin_detail()
            ]
        }
        return output


#endregion

# Вызов функции для инициализации базы данных
#Database.start_database()
#
#Database.insert_data()
#print(Database.get_gagarin_mission())
