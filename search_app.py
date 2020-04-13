import pygame
import requests
import sys
import os

import math

from distance import lonlat_distance
from geo import reverse_geocode
from bis import find_business

# Подобранные констатны для поведения карты.
LAT_STEP = 0.008  # Шаги при движении карты по широте и долготе
LON_STEP = 0.02
coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
coord_to_geo_y = 0.0000428


def ll(x, y):
    return "{0},{1}".format(x, y)


# Структура для хранения результатов поиска:
# координаты объекта, его название и почтовый индекс, если есть.

class SearchResult(object):
    def __init__(self, point, address, postal_code=None):
        self.point = point
        self.address = address
        self.postal_code = postal_code


# Параметры отображения карты:
# координаты, масштаб, найденные объекты и т.д.

class MapParams(object):
    # Параметры по умолчанию.
    def __init__(self):
        self.lat = 55.729738  # Координаты центра карты на старте.
        self.lon = 37.664777
        self.zoom = 15  # Масштаб карты на старте.
        self.type = "map"  # Тип карты на старте.

        self.search_result = None  # Найденный объект для отображения на карте.
        self.use_postal_code = False

    # Преобразование координат в параметр ll
    def ll(self):
        return ll(self.lon, self.lat)

    # Обновление параметров карты по нажатой клавише.
    def update(self, event):
        if event.key == 280 and self.zoom < 19:  # PG_UP
            self.zoom += 1
        elif event.key == 281 and self.zoom > 2:  # PG_DOWN
            self.zoom -= 1
        elif event.key == 276:  # LEFT_ARROW
            self.lon -= LON_STEP * math.pow(2, 15 - self.zoom)
        elif event.key == 275:  # RIGHT_ARROW
            self.lon += LON_STEP * math.pow(2, 15 - self.zoom)
        elif event.key == 273 and self.lat < 85:  # UP_ARROW
            self.lat += LAT_STEP * math.pow(2, 15 - self.zoom)
        elif event.key == 274 and self.lat > -85:  # DOWN_ARROW
            self.lat -= LAT_STEP * math.pow(2, 15 - self.zoom)
        elif event.key == 49:  # 1
            self.type = "map"
        elif event.key == 50:  # 2
            self.type = "sat"
        elif event.key == 51:  # 3
            self.type = "sat,skl"
        elif event.key == 127:  # DELETE
            self.search_result = None
        elif event.key == 277:  # INSERT
            self.use_postal_code = not self.use_postal_code

        if self.lon > 180: self.lon -= 360
        if self.lon < -180: self.lon += 360

    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * coord_to_geo_x * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * coord_to_geo_y * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.zoom)
        return lx, ly

    # Добавить результат геопоиска на карту.
    def add_reverse_toponym_search(self, pos):
        point = self.screen_to_geo(pos)
        toponym = reverse_geocode(ll(point[0], point[1]))
        self.search_result = SearchResult(
            point,
            toponym["metaDataProperty"]["GeocoderMetaData"]["text"] if toponym else None,
            toponym["metaDataProperty"]["GeocoderMetaData"]["Address"].get("postal_code") if toponym else None)

    # Добавить результат поиска организации на карту.
    def add_reverse_org_search(self, pos):
        self.search_result = None
        point = self.screen_to_geo(pos)
        org = find_business(ll(point[0], point[1]))
        if not org:
            return

        org_point = org["geometry"]["coordinates"]
        org_lon = float(org_point[0])
        org_lat = float(org_point[1])

        # Проверяем, что найденный объект не дальше 50м от места клика.
        if lonlat_distance((org_lon, org_lat), point) <= 50:
            self.search_result = SearchResult(point, org["properties"]["CompanyMetaData"]["name"])


# Создание карты с соответствующими параметрами.
def load_map(mp):
    map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}".format(ll=mp.ll(), z=mp.zoom, type=mp.type)
    if mp.search_result:
        map_request += "&pt={0},{1},pm2grm".format(mp.search_result.point[0], mp.search_result.point[1])

    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    return map_file


# Создание холста с текстом.
def render_text(text):
    font = pygame.font.Font(None, 30)
    return font.render(text, 1, (100, 0, 100))


def main():
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))

    # Заводим объект, в котором будем хранить все параметры отрисовки карты.
    mp = MapParams()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:  # Выход из программы
            break
        elif event.type == pygame.KEYUP:  # Обрабатываем различные нажатые клавиши.
            mp.update(event)
        elif event.type == pygame.MOUSEBUTTONUP:  # Выполняем поиск по клику мышки.
            if event.button == 1:  # LEFT_MOUSE_BUTTON
                mp.add_reverse_toponym_search(event.pos)
            elif event.button == 3:  # RIGHT_MOUSE_BUTTON
                mp.add_reverse_org_search(event.pos)
        else:
            continue

        # Загружаем карту, используя текущие параметры.
        map_file = load_map(mp)

        # Рисуем картинку, загружаемую из только что созданного файла.
        screen.blit(pygame.image.load(map_file), (0, 0))

        # Добавляем подписи на экран, если они нужны.
        if mp.search_result:
            if mp.use_postal_code and mp.search_result.postal_code:
                text = render_text(mp.search_result.postal_code + ", " + mp.search_result.address)
            else:
                text = render_text(mp.search_result.address)
            screen.blit(text, (20, 400))

        # Переключаем экран и ждем закрытия окна.
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


if __name__ == "__main__":
    main()
