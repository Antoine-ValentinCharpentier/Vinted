from requests.exceptions import HTTPError
from typing import List, Dict
from time import sleep
import pandas as pd
import os
import requests

from requester import Requester
from item import Item
from utils import parse_url, create_directory_structure, max_catalog_depth, collect_catalogs

from  constants import VINTED_API_URL, VINTED_PRODUCTS_ENDPOINT, VINTED_DTOS_ENDPOINT, VINTED_URL_PAGE_CATALOG

class Vinted:
    def __init__(self, proxy=None, request_delay=0.5, download_images = False):   
        self.requester = Requester()
        if proxy is not None:
            self.requester.session.proxies.update(proxy)
        
        self.request_delay = request_delay
        self.download_images = download_images
        
        self.catalogs = self.get_catalogs()

    def search(self, url_research, nb_items_page: int = 96, starting_page: int = 0, ending_page: int = 1, filename: str = "./data/results.csv", time: int = None) -> List[Item]:
        results = []
        
        if ending_page < starting_page:
            print(f"Ending page {ending_page} is less than starting page {starting_page}, inverting values.")
            starting_page, ending_page = ending_page, starting_page
        if starting_page < 1:
            print(f"Starting page {starting_page} is invalid, resetting to 1.")
            starting_page = 1
            
        params_request = parse_url(url_research, nb_items_page, 1, time)
        if int(params_request['catalog_ids']) not in self.catalogs.keys(): 
            print(f"Please enter the ID of the deepest catalog. It seems that the catalog with ID {int(params_request['catalog_ids'])} has sub-catalogs.")
            return []
        
        try:
            for page in range(starting_page, ending_page+1):
                params_request["page"] = page
                response = self.requester.get(
                    url=f"{VINTED_API_URL}/{VINTED_PRODUCTS_ENDPOINT}", 
                    params=params_request
                )
                response.raise_for_status()
                items = response.json().get("items", [])

                section_names = self.catalogs[int(params_request['catalog_ids'])]
                
                results_page = [Item(_item, section_names=section_names) for _item in items]
                results += results_page
                sleep(self.request_delay)

            self.save_results(results, filename)
            return results
        except HTTPError as err:
            raise err
        
    def search_all(self, nb_items_page: int = 96, nb_page: int = 10, excludes_catalogs_names: List[str] = [], folder_results: str = "./data",) -> List[Item]:
        results = []
        
        catalogs_filtered = {
            key: value
            for key, value in self.catalogs.items()
            if not set(value) & set(excludes_catalogs_names)
        }
        
        for catalog_id, sections_names in catalogs_filtered.items():
            print('>> Catalog : ', ', '.join(sections_names))
            url = VINTED_URL_PAGE_CATALOG.replace('{{CATALOG_ID}}', str(catalog_id))
            results_catalogs = self.search(url, nb_items_page, starting_page=1, ending_page=nb_page, filename=f"{folder_results}/results_{catalog_id}.csv")
            results += results_catalogs
        
        return results
            
    def get_dtos(self, catalog_id: int = 1206) -> Dict:
        try:
            response = self.requester.get(
                url=f"{VINTED_API_URL}/{VINTED_DTOS_ENDPOINT}?catalog[]={catalog_id}&supported_display_types=list,list_search,grid,hybrid_price,exposed_filter,prefix_image", 
            )
            response.raise_for_status()
            dtos = response.json()
            return dtos
        except HTTPError as err:
            raise err
        
    def get_catalogs(self) -> Dict[str, List[str]]:
        dtos = self.get_dtos()
        nb_max_section = max_catalog_depth(dtos)
        catalogs = {}
        
        for catalog_root in dtos['dtos']['catalogs']:
            collect_catalogs(catalog_root, [], nb_max_section, catalogs)
        
        return catalogs
    
    def save_results(self, items: List[dict], filename: str):
        create_directory_structure("/".join(filename.split('/')[:-1]))
        
        data = [item.to_dict() for item in items]
        df = pd.DataFrame(data)
        df['path_downloaded_photo'] = ''
        
        if self.download_images:
            for idx, row in df.iterrows():
                photo_extension = row['photo'].split('?')[0].split('.')[-1]
                complete_filepath = os.path.join(
                    "/".join(filename.split('/')[:-1]), 'photos', 
                    row['section'], row['sub_section'], row['sub_sub_section'], 
                    f"{row['id']}.{photo_extension}"
                )
                if not os.path.exists(complete_filepath):
                    create_directory_structure(os.path.dirname(complete_filepath))
                    try:
                        response = requests.get(url=row['photo'])
                        response.raise_for_status()  
                        with open(complete_filepath, 'wb') as img:
                            img.write(response.content)
                        df.at[idx, 'path_downloaded_photo'] = complete_filepath
                    except requests.RequestException as e:
                        print(f'Error while downloading: {row["photo"]}, error: {e}')
        
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")