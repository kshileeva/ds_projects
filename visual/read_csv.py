import pandas as pd

def dropping_columns(data, cols: list):
    return data[cols]


data1 = pd.read_csv('11_2021_EN.csv', delimiter=';', header=None, names=['text', 'Country', 'Country code', 'Currencies', 'ISO code', 'Rate', 'Note'])
data2 = pd.read_csv('12_2021_EN.csv', delimiter=';', header=None, names=['text', 'Country', 'Country code', 'Currencies', 'ISO code', 'Rate', 'Note'])

data1 = data1.drop(0)
data2 = data2.drop(0)
new1 = dropping_columns(data1, ['Country', 'Country code', 'ISO code', 'Rate'])
new2 = dropping_columns(data1, ['Country', 'Country code', 'ISO code', 'Rate'])
print(new1)
