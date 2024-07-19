from urllib.parse import urlparse, parse_qsl
import pandas as pd
import os
from typing import List, Dict

from item import Item

def parse_url(url_research, nbItems=20, page=1, time=None) -> Dict:
    query_data = urlparse(url_research).query
    querys = parse_qsl(query_data)

    params = {
        "search_text": get_param(querys, "search_text", join_with="+"),
        "catalog_ids": get_param(querys, "catalog[]"),
        "color_ids": get_param(querys, "color_ids[]"),
        "brand_ids": get_param(querys, "brand_ids[]"),
        "size_ids": get_param(querys, "size_ids[]"),
        "material_ids": get_param(querys, "material_ids[]"),
        "status_ids": get_param(querys, "status[]"),
        "country_ids": get_param(querys, "country_ids[]"),
        "city_ids": get_param(querys, "city_ids[]"),
        "is_for_swap": get_param(querys, "disposal[]", join_with=",", default="1"),
        "currency": get_param(querys, "currency"),
        "price_to": get_param(querys, "price_to"),
        "price_from": get_param(querys, "price_from"),
        "page": page,
        "per_page": nbItems,
        "order": get_param(querys, "order"),
        "time": time
    }

    return params
    
def get_param(querys, key, join_with=',', default=''):
    """Extrait les valeurs associées à une clé, les joint avec un séparateur et retourne une chaîne."""
    return join_with.join(map(str, [value for k, value in querys if k == key])) or default

def save_to_csv(items: List[Item], filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = [item.to_dict() for item in items]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Results saved to {filename}")