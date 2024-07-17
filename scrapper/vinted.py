from urllib.parse import urlparse, parse_qsl
from requests.exceptions import HTTPError
from typing import List, Dict

from requester import Requester
from item import Item
from utils import get_param

from  constants import VINTED_API_URL, VINTED_PRODUCTS_ENDPOINT, VINTED_DTOS_ENDPOINT, VINTED_URL_PAGE_CATALOG

class Vinted:
    def __init__(self, proxy=None):
        self.requester = Requester()
        if proxy is not None:
            self.requester.session.proxies.update(proxy)

    def search(self, url_research, nb_items_page: int = 96, starting_page: int = 0, ending_page: int = 1, time: int = None, want_json: bool = False) -> List[Item]:
        results = []
        
        if ending_page < starting_page:
            print(f"Ending page {ending_page} is less than starting page {starting_page}, inverting values.")
            starting_page, ending_page = ending_page, starting_page
        if starting_page < 1:
            print(f"Starting page {starting_page} is invalid, resetting to 1.")
            starting_page = 1
        
        try:
            for page in range(starting_page, ending_page+1):
                params_request = self.parse_url(url_research, nb_items_page, page, time)

                response = self.requester.get(
                    url=f"{VINTED_API_URL}/{VINTED_PRODUCTS_ENDPOINT}", 
                    params=params_request
                )
                response.raise_for_status()
                items = response.json().get("items", [])

                results_page = [Item(_item) for _item in items] if not want_json else items
                results += results_page

            return results
        except HTTPError as err:
            raise err
        
    def search_all(self, nb_items_page: int = 96, nb_page: int = 10, excludes_catalogs_names: List[str] = []) -> List[Item]:
        results = []
        catalogs_ids = self.get_catalogs_ids(excludes_catalogs_names)
        
        for catalog_id in catalogs_ids:
            print('>> Catalog id n°', catalog_id)
            url = VINTED_URL_PAGE_CATALOG.replace('{{CATALOG_ID}}', str(catalog_id))
            print(url)
            results_catalogs = self.search(url, nb_items_page, starting_page=1, ending_page=nb_page, want_json=True)
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

    def parse_url(self, url_research, nbItems=20, page=1, time=None) -> Dict:
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