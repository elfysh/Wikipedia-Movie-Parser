import pandas as pd

# Удаляем фильмы, в которых хотя бы 1 параметр неизвестен
df = pd.read_json('movies_data_v3.json')
df = df.dropna()

# Оставляем только одного режиссера у фильма
df['director'] = df['director'].str.split(',').str.get(0)

# Форматируем жанры
df['genre'] = df['genre'].str.split('|').apply(lambda x: ','.join([genre.capitalize() for genre in x]))

#Сохраняем в json
df['year'] = df['year'].astype(int)
df.to_json('data_cleaned.json', orient='records', force_ascii=False)
