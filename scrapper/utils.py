import pandas as pd
import os
from typing import List

from item import Item

def get_param(querys, key, join_with=',', default=''):
    """Extrait les valeurs associées à une clé, les joint avec un séparateur et retourne une chaîne."""
    return join_with.join(map(str, [value for k, value in querys if k == key])) or default

def save_to_csv(items: List[Item], filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(items)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Results saved to {filename}")