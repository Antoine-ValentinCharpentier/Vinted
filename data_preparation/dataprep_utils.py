import os
import pandas as pd
from typing import List

def merge_results(folder_path: str = "../data", file_path_output: str = "../data/merged_results.csv", percentage: int=100) -> pd.DataFrame :
    if not (0 <= percentage <= 100):
        print('The percentage must have a value between 0 and 100!')
        percentage = max(0, min(percentage, 100))
    
    try:
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f != os.path.basename(file_path_output)]
    except FileNotFoundError:
        print(f"The folder {folder_path} does not exist.")
        return None

    data_frames = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        num_rows = int(len(df) * (percentage / 100))
        df = df.head(num_rows)
        data_frames.append(df)

    merged_df = pd.concat(data_frames, ignore_index=True)

    merged_df.to_csv(file_path_output, index=False)

    print(f'Files merged and saved inside {file_path_output}')
    
    return merged_df
    
def remove_useless_columns(df: pd.DataFrame, columns_to_drop : List[str]=['user_url', 'photo', 'url', 'title', 'id', 'content_source', 'user_id']) -> pd.DataFrame :
    return df.drop(columns=columns_to_drop)

def preprocessing(folder_path: str = "../data"):
    df = merge_results(folder_path, file_path_output="../data/merged_results.csv", percentage=100)
    df = remove_useless_columns(df, columns_to_drop=['user_url', 'photo', 'url', 'title', 'id', 'content_source', 'user_id'])
    return df