from urllib.parse import urlparse, parse_qsl
import os
import pandas as pd
import threading
import requests

from typing import Dict

# Parsing URL

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

# Catalogs

def get_catalog_depth(catalog, current_depth=1):
    if 'catalogs' in catalog and catalog['catalogs']:
        return max(get_catalog_depth(sub_catalog, current_depth + 1) for sub_catalog in catalog['catalogs'])
    else:
        return current_depth

def max_catalog_depth(dtos):
    return max(get_catalog_depth(catalog) for catalog in dtos['dtos']['catalogs'])

def collect_catalogs(catalog, current_path, nb_max_section, catalogs):
    current_path.append(catalog['title'])
    
    if 'catalogs' in catalog and catalog['catalogs']:
        for sub_catalog in catalog['catalogs']:
            collect_catalogs(sub_catalog, current_path.copy(), nb_max_section, catalogs)
    else:
        while len(current_path) < nb_max_section:
            current_path.append("")
        catalogs[catalog['id']] = current_path

#  IMAGES

def create_directory_structure(path: str):
    os.makedirs(os.path.join(path), exist_ok=True)
    
def download_photo(row, filename, results, idx):
    photo_extension = row['photo'].split('?')[0].split('.')[-1]
    
    sections = [row[col] for col in row.index if col.endswith('section') and pd.notna(row[col]) and row[col]]
    
    complete_filepath = os.path.join(
        "/".join(filename.split('/')[:-1]), 'photos', 
        *sections, 
        f"{row['id']}.{photo_extension}"
    )
    
    if not os.path.exists(complete_filepath):
        create_directory_structure(os.path.dirname(complete_filepath))
        try:
            response = requests.get(url=row['photo'])
            response.raise_for_status()  
            with open(complete_filepath, 'wb') as img:
                img.write(response.content)
            results[idx] = complete_filepath
        except requests.RequestException as e:
            print(f'Error while downloading: {row["photo"]}, error: {e}')
            results[idx] = None
    else:
        results[idx] = complete_filepath

def download_photos_concurrently(df, filename, max_workers=10):
    threads = []
    path_downloaded_images = [''] * len(df)

    for idx, row in df.iterrows():
        if len(threads) >= max_workers:
            for thread in threads:
                thread.join() 
            threads = []

        thread = threading.Thread(target=download_photo, args=(row, filename, path_downloaded_images, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() 

    df['path_downloaded_photo'] = path_downloaded_images
                
                