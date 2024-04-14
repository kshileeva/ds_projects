import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df_train = pd.read_csv('depot_data/train.csv', encoding='ISO-8859-1')
df_attr = pd.read_csv('depot_data/attributes.csv', encoding='ISO-8859-1')


def total_num_pairs(df=df_train) -> str:
    pairs = df[['product_title', 'search_term']]
    unique_pairs = pairs.drop_duplicates()
    num_unique_pairs = unique_pairs.shape[0]
    return f'Number of unique product-query pairs:{num_unique_pairs}'


def unique_products(df=df_train) -> str:
    num = df['product_title'].nunique()
    return f'Number of unique products: {num}'


def top_2_occur_product(df=df_train) -> str:
    product_counts = df['product_title'].value_counts()
    top_two_products = product_counts.head(2)
    return f'Top two occurring products and their counts in column:"\n{top_two_products}'


def relevance_mean(df=df_train) -> str:
    mean = df['relevance'].mean()
    return f'Mean: {mean}'


def standard_dev(num: int = len(df_train['relevance']), points: list[float] = df_train['relevance'].tolist(),
                 mean: float = df_train['relevance'].mean()) -> str:
    variance = 0
    for point in points:
        variance += pow((point - mean), 2)
    return f'Standard deviation: {math.sqrt((variance / (num - 1)))}'


def relevance_med(df=df_train) -> str:
    return f'Median: {df["relevance"].median()}'


def boxplot(df=df_train):
    relevance_values = df['relevance'].tolist()
    median_value = np.median(relevance_values)
    plt.figure(figsize=(4, 3))
    plt.boxplot(relevance_values, medianprops=dict(color='red', linewidth=2))
    plt.title('Distribution of Relevance Values')
    plt.ylabel('Relevance Score')
    plt.grid(True)
    plt.text(1, median_value, f'Median = {median_value:.2f}', ha='left', va='bottom', color='red')
    plt.show()


def top_brand_names(df=df_attr) -> str:
    name_cnt = df['name'].value_counts()
    top_names = name_cnt.head(5)
    return f'Top 5 occurring brand names:\n{top_names}'


print(total_num_pairs())
print(unique_products())
print(top_2_occur_product())
print(relevance_mean())
print(standard_dev())
print(relevance_med())
print(top_brand_names())
boxplot()
