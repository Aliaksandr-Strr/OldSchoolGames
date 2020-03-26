# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет только две локации и не будет мобов
# (то есть в коренном json-объекте содержится список, содержащий только два json-объекта и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date

import csv
import json
import datetime
import re
from decimal import Decimal

remaining_time = '123456.0987654321'
# если изначально не писать число в виде строки - теряется точность!
field_names = ['current_location', 'current_experience', 'current_date']


class Game:

    def __init__(self):
        self.file_route = 'rpg.json'
        self.route = None
        self.current_location = None
        self.current_experience = 0
        self.remaining_time = Decimal('123456.0987654321')
        self.requirement_win = 0
        self.loss = 0
        self.variants_occasion = []
        self.potential_move = []
        self.monsters = []
        self.current_date = Decimal('0')
        self.time_start_game = 0
        self.game_result = [['current_location', 'current_experience', 'current_date']]
        with open(self.file_route, 'r') as f:
            self.route = json.load(f)
        for section in self.route:
            self.current_location = section

    def enter_location(self):
        number_cave = re.search(r".\d+", self.current_location)
        print(f'Вы находитесь в локации № {number_cave.group()}')
        transition_time = re.search(r"\d+$", self.current_location)
        self.remaining_time -= Decimal(transition_time.group())
        self.time_start_game += int(transition_time.group())
        self.current_date = str(datetime.timedelta(seconds=self.time_start_game))
        self.game_result.append([self.current_location, self.current_experience, self.current_date])
        print(f'У вас {self.current_experience} опыта и осталось {self.remaining_time} секунд до наводнения')
        print(f'Прошло времени: {self.current_date}')

    def fight(self):
        print('Вы выбрали сражаться с монстром')
        for monster in self.monsters:
            experience = re.search(r"\d+", monster)
            time_killing = re.search(r'\d+$', monster)
            self.current_experience += int(experience.group())
            self.remaining_time -= Decimal(time_killing.group())
            self.time_start_game += int(time_killing.group())
            self.current_date = str(datetime.timedelta(seconds=self.time_start_game))
        print('Вы победили всех монстров')
        print(f'У вас {self.current_experience} опыта и осталось {self.remaining_time} секунд до наводнения')
        print(f'Прошло времени: {self.current_date}')
        self.navigate_to_locations()

    def open_hatch(self):
        transition_time = re.search(r"\d+.\d+$", self.current_location)
        self.remaining_time -= Decimal(transition_time.group())
        print(f'До наводнения оставалось {self.remaining_time}')
        if self.current_experience >= 280 and self.remaining_time > 0:
            self.requirement_win = 1
            print('Победа!!!')
            self.victory()
        else:
            self.loss = 1
            print('\nВам не хватило опыта открыть люк!')
            print('\nВы ПРОИГРАЛИ!!! АХхаХА')
            print('\nНачнем же сначала!\n')
            self.game_over()

    def action(self):
        self.potential_move = []
        self.monsters = []
        print('Внутри вы видите:')
        self.variants_occasion = self.route[self.current_location]
        for occasion in range(len(self.variants_occasion)):
            for event in self.variants_occasion[occasion]:
                if event == 'M':
                    print(f'— Монстр {self.variants_occasion[occasion]}')
                    self.monsters.append(self.variants_occasion[occasion])
                    break
                if event == 'B':
                    print(f'— Босс {self.variants_occasion[occasion]}')
                    self.monsters.append(self.variants_occasion[occasion])
                    break
                self.potential_move.append(event)
                print(f'— Вход в локацию: {event}')
        print(''' Выберите действие:
                 1.Атаковать монстра
                 2.Перейти в другую локацию
                 3.Сдаться и выйти из игры''')

    def navigate_to_locations(self):
        print('Вы выбрали переход в локацию')
        select_cave = len(self.potential_move)
        if select_cave < 1:
            print('\nНет возможных локаций для перехода')
            print('\nВы ПРОИГРАЛИ!!! АХхаХА')
            print('\nНачнем же сначала!\n')
            self.loss = 1
            self.game_over()
        elif select_cave > 1:
            while True:
                select = int(input('Выберете локацию для перехода'))
                for cave in range(1, select_cave + 1):
                    if select == cave:
                        if len(self.monsters):
                            self.route = self.variants_occasion[cave]
                        else:
                            self.route = self.variants_occasion[cave - 1]
                        self.current_location = self.potential_move[cave - 1]
                        break
                break
        elif select_cave == 1:
            self.route = self.variants_occasion[len(self.monsters)]
            self.current_location = self.potential_move[0]
            if self.current_location == "Hatch_tm159.098765432":
                self.open_hatch()

    def write_file(self):
        with open('way', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter='#')
            for i in self.game_result:
                writer.writerow(i)

    def game_over(self):
        return self.loss

    def victory(self):
        return self.requirement_win


def game_engine():
    game = Game()
    while True:
        if game.victory():
            game.write_file()
            break
        elif game.game_over():
            game.write_file()
            game = Game()
        else:
            game.enter_location()
            game.action()
            try:
                selection = int(input())
                if selection == 1:
                    game.fight()
                elif selection == 2:
                    game.navigate_to_locations()
                elif selection == 3:
                    print('Спасибо за игру')
                    break
                else:
                    print('Введите цифру от 1 до 3')
            except ValueError:
                print('Вы ввели не число')


game_engine()
