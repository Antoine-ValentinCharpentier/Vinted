VINTED_API_URL = f"https://www.vinted.fr/api/v2"
VINTED_PRODUCTS_ENDPOINT = "catalog/items"
VINTED_AUTH_URL = f"https://www.vinted.fr/auth/token_refresh"
VINTED_DTOS_ENDPOINT = "catalog/initializers"

MAX_RETRIES = 3
HEADERS = {
            "User-Agent": "PostmanRuntime/7.28.4",
            "Host": "www.vinted.fr",
}

VINTED_URL_PAGE_CATALOG = "https://www.vinted.fr/catalog?catalog[]={{CATALOG_ID}}&order=newest_first"