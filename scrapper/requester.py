import requests
from requests.exceptions import HTTPError
from constants import HEADERS, MAX_RETRIES, VINTED_AUTH_URL

class Requester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.setAuthCookies()

    def get(self, url, params=None):
        for tried in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params)

                if response.status_code == 401 and tried < MAX_RETRIES:
                    print(f"Cokkies invalid retrying {tried}/{MAX_RETRIES}")
                    self.setAuthCookies()
                elif response.status_code == 200 or tried == MAX_RETRIES:
                    return response
            except HTTPError as err:
                if tried == MAX_RETRIES:
                    raise err

    def post(self,url, params=None):
        response = self.session.post(url, params)
        response.raise_for_status()
        return response

    def setAuthCookies(self):
        self.session.cookies.clear_session_cookies()
        try:
            self.post(VINTED_AUTH_URL)
            print("Auth cookies define")
        except Exception as e:
            print(f"Error getting Auth Cookies : {e}")
