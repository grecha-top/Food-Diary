
# FOOD-DIARY
-  Это удобный сборник блюд с их КБЖУ. Также есть возможноть добавлять аллергены(можно создать свои или воспользоваться глобальными аллергенами)

## Features
1. Вход/регистрация
2. Управление аллергенами
3. Упраление блюдами
4. Удобная фильтрация блюд по разным параметрам
5. Возможность добавления фото к блюду

## Tech Stack
1. Python
2. Django
3. SQLite
4. HTML
5. CSS

## Installation

#### Linux/MacOS
1. Склонируйте репозиторий
```sh
git clone https://github.com/mnonessss/Food-Diary
```
2. Перейдите в папку
```sh
cd Food-Diary
```
3. Создайте виртуальное окружение
```python
python -m venv venv
```
4. Установите Django(при необходимости)
```python
pip install django
```
4. Активируйте виртуальное окружение
```sh
source venv/bin/activate #scripts
```
5. Создайте и примените миграции
```python
python manage.py makemigrations
python manage.py migrate
```
6. Запустите приложение
```python
python manage.py runserver
```

### Windows
1. Склонируйте репозиторий
```sh
git clone https://github.com/mnonessss/Food-Diary
```
2. Перейдите в папку
```sh
cd Food-Diary
```
3. Создайте виртуальное окружение
```python
python -m venv venv
```
4. Установите Django(при необходимости)
```python
pip install django
```
4. Активируйте виртуальное окружение
```sh
source venv/scripts/activate 
```
5. Создайте и примените миграции
```python
python manage.py makemigrations
python manage.py migrate
```
6. Запустите приложение
```python
python manage.py runserver
```


## Screenshots
1. Приветственная страница
<img width="1857" height="913" alt="Pasted image 20251215152818" src="https://github.com/user-attachments/assets/674ab61a-95f2-4eda-b21c-32cd6fd257b3" />

2. Профиль
<img width="1881" height="916" alt="Pasted image 20251215152948" src="https://github.com/user-attachments/assets/52f92563-3c59-4ffe-9c3f-d892c3988440" />

3.Мои блюда
<img width="1177" height="829" alt="Pasted image 20251215153030" src="https://github.com/user-attachments/assets/42554aac-893a-47d5-9670-fbb194ebf2db" />

4.Аллергены
<img width="915" height="465" alt="Pasted image 20251215153052" src="https://github.com/user-attachments/assets/b6bde4f0-b640-4a02-8faa-e7490b144d72" />



## ER-диаграмма
<img width="1834" height="859" alt="Pasted image 20251215154225" src="https://github.com/user-attachments/assets/0b5fe1e8-38ed-42ab-8ece-fa08a4ce82de" />



## Архитектурная диаграмма
<img width="1279" height="717" alt="Pasted image 20251215154303" src="https://github.com/user-attachments/assets/6726af8c-2355-4458-a56a-eae991663c7f" />

