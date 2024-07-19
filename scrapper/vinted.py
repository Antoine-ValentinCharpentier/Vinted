from requests.exceptions import HTTPError
from typing import List, Dict
from time import sleep

from requester import Requester
from item import Item
from utils import parse_url, save_to_csv

from  constants import VINTED_API_URL, VINTED_PRODUCTS_ENDPOINT, VINTED_DTOS_ENDPOINT, VINTED_URL_PAGE_CATALOG

class Vinted:
    def __init__(self, request_delay=0.5, proxy=None):
        self.request_delay = request_delay
        self.requester = Requester()
        if proxy is not None:
            self.requester.session.proxies.update(proxy)

    def search(self, url_research, nb_items_page: int = 96, starting_page: int = 0, ending_page: int = 1, filename: str = "./data/results.csv", time: int = None) -> List[Item]:
        results = []
        
        if ending_page < starting_page:
            print(f"Ending page {ending_page} is less than starting page {starting_page}, inverting values.")
            starting_page, ending_page = ending_page, starting_page
        if starting_page < 1:
            print(f"Starting page {starting_page} is invalid, resetting to 1.")
            starting_page = 1
        
        try:
            for page in range(starting_page, ending_page+1):
                params_request = parse_url(url_research, nb_items_page, page, time)

                response = self.requester.get(
                    url=f"{VINTED_API_URL}/{VINTED_PRODUCTS_ENDPOINT}", 
                    params=params_request
                )
                response.raise_for_status()
                items = response.json().get("items", [])

                results_page = [Item(_item) for _item in items]
                results += results_page
                sleep(self.request_delay)

            save_to_csv(results, filename)
            return results
        except HTTPError as err:
            raise err
        
    def search_all(self, nb_items_page: int = 96, nb_page: int = 10, excludes_catalogs_names: List[str] = [], folder_results: str = "./data",) -> List[Item]:
        results = []
        catalogs_ids = self.get_catalogs_ids(excludes_catalogs_names)
        
        for catalog_id in catalogs_ids:
            print('>> Catalog id n°', catalog_id)
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
        
    def get_catalogs_ids(self, excludes_catalogs_names: List[str] = [] ) -> List[int]:
        dtos = self.get_dtos()
        catalogs_ids = []
        for catalogs_root in dtos['dtos']['catalogs']:
            if catalogs_root['title'] not in excludes_catalogs_names:
                for sub_catalogs in catalogs_root['catalogs']:
                    if sub_catalogs['title'] not in excludes_catalogs_names:
                        for sub_sub_catalogs in sub_catalogs['catalogs']:
                            if sub_sub_catalogs['title'] not in excludes_catalogs_names:
                                catalogs_ids.append(sub_sub_catalogs['id'])
        return catalogs_ids
