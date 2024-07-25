import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame

def display_unique_values(df: DataFrame) -> None:
    category_columns = df.select_dtypes(include=['object', 'category']).columns

    # Display textual examples and the number of unique values
    unique_value_counts = []
    for variable in category_columns:
        unique = df[variable].unique()
        print(f"Number of unique values for '{variable}': {len(unique)}")
        if len(unique) < 15:
            print(f' -> All values : {unique}')
        else:
            print(f'- Example of value : {unique[1]}')
        unique_value_counts.append((variable, len(unique)))

    # Display a graph
    unique_counts_df = pd.DataFrame(unique_value_counts, columns=['Feature', 'Unique Values'])

    plt.figure(figsize=(10, 6))
    plt.barh(unique_counts_df['Feature'], unique_counts_df['Unique Values'], color='skyblue')

    for index, value in enumerate(unique_counts_df['Unique Values']):
        plt.text(value, index, str(value), va='center', ha='left', color='black')

    plt.xlabel('Number of unique values')
    plt.ylabel('Features')
    plt.title('Number of unique values per feature')
    plt.xscale('log')
    plt.grid(axis='x')

    plt.show()
