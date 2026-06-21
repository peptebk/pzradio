import json
import os

DB_FILE = "stations.json"

def load_stations():
    """Загружает список станций из JSON файла"""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Ошибка: файл stations.json повреждён")
        return []

def save_stations(stations):
    """Сохраняет список станций в JSON файл"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=4)

def add_station(name, url):
    """Добавляет новую радиостанцию"""
    stations = load_stations()
    stations.append({"name": name, "url": url})
    save_stations(stations)
    print(f"Станция '{name}' добавлена")

def delete_station(index):
    """Удаляет станцию по индексу (начиная с 0)"""
    stations = load_stations()
    if 0 <= index < len(stations):
        removed = stations.pop(index)
        save_stations(stations)
        print(f"Станция '{removed['name']}' удалена")
    else:
        print("Неверный индекс")

def get_station_url(choice):
    """Возвращает URL станции по номеру выбора (начиная с 1)"""
    stations = load_stations()
    if not stations:
        return None
    if 1 <= choice <= len(stations):
        return stations[choice - 1]["url"]
    return None

def list_stations():
    """Возвращает список станций для отображения"""
    stations = load_stations()
    if not stations:
        return ["База пуста"]
    return [f"{i+1}. {s['name']}" for i, s in enumerate(stations)]

def get_stations_count():
    """Возвращает количество станций"""
    return len(load_stations())