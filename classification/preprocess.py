import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

from config import random_state

def encode_labels(df):
    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    
    section_columns = [col for col in df.columns if col.endswith('section')]
    
    encoded_labels = ohe.fit_transform(df[section_columns])
    
    encoded_labels_df = pd.DataFrame(encoded_labels, columns=[
        f'{col}_{cat}' for col in section_columns for cat in ohe.categories_[section_columns.index(col)]
    ])
    
    df = pd.concat([df, encoded_labels_df], axis=1)
    df = df.drop(columns=section_columns)
    
    section_categories = {section_columns[idx_section]:cat for idx_section, cat in enumerate(ohe.categories_)}
    
    return df, section_categories

def split_data(df):
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=random_state)
    train_df, val_df = train_test_split(train_df, test_size=0.2, random_state=random_state)
    return train_df, val_df, test_df


