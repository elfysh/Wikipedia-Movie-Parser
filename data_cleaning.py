import pandas as pd

# Удаляем фильмы, в которых хотя бы 1 параметр неизвестен/удаляем записи с неизвестными режиссерами
df = pd.read_json('movies_data_v3.json')
mask = ~df['director'].str.contains('неизвестно|неизвестен|см. ниже|не указан|отсутствует', case=False, na=False)

df = df[mask]
df = df.dropna()

# Оставляем только одного режиссера у фильма
df['director'] = df['director'].str.split(',').str.get(0)

# Форматируем жанры
df['genre'] = df['genre'].str.split('|').apply(lambda x: ','.join([genre.capitalize() for genre in x]))

#Сохраняем в json и в csv
df['year'] = df['year'].astype(int)
df.to_json('data_cleaned.json', orient='records', force_ascii=False)
df.to_csv('data_cleaned.csv', index=False, encoding='utf-8')
