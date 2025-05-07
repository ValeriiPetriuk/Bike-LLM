import  pandas as pd

df = pd.read_csv("data/Transactions_cleaned.csv", on_bad_lines="skip")

print(df['listPrice'].min(), df['listPrice'].max())

# df.to_csv('data/Transactions_cleaned.csv', index=False)

import csv
import random

# Параметри
brands = ['Solex', 'Trek Bicycles', 'OHM Cycles', 'Norco Bicycles', 'Giant Bicycles', 'WeareA2B']
product_lines = ['Standard', 'Road', 'Mountain', 'Touring']
product_sizes = ['medium', 'large', 'small']

# Випадкове число записів, наприклад, 100
num_rows = 100

# Створення CSV
with open('products.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['productid', 'brand', 'productLine', 'productSize', 'listPrice'])

    for product_id in range(1, num_rows + 1):
        brand = random.choice(brands)
        product_line = random.choice(product_lines)
        product_size = random.choice(product_sizes)
        list_price = round(random.uniform(12.01, 2091.47), 2)
        writer.writerow([product_id, brand, product_line, product_size, list_price])

print("Файл products.csv успішно створено.")
