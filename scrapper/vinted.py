from urllib.parse import urlparse, parse_qsl
from requests.exceptions import HTTPError
from typing import List, Dict

from requester import Requester
from item import Item
from utils import get_param

from  constants import VINTED_API_URL, VINTED_PRODUCTS_ENDPOINT

class Vinted:
    def __init__(self, proxy=None):
        self.requester = Requester()
        if proxy is not None:
            self.requester.session.proxies.update(proxy)

    def search(self, url_research, nbItems: int = 20, page: int = 1, time: int = None, json: bool = False) -> List[Item]:
        try:
            params_request = self.parseUrl(url_research, nbItems, page, time)

            response = self.requester.get(
                url=f"{VINTED_API_URL}/{VINTED_PRODUCTS_ENDPOINT}", 
                params=params_request
            )
            response.raise_for_status()
            items = response.json().get("items", [])

            return [Item(_item) for _item in items] if not json else items

        except HTTPError as err:
            raise err

    def parseUrl(self, url_research, nbItems=20, page=1, time=None) -> Dict:
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