from typing import List, Dict

class Item:
    def __init__(self, data: Dict, section_names : List[str] = []):
        self.id = data.get("id", None)
        
        self.title = data.get("title", "")
        self.url = data.get("url", "")
        photo_data = data.get("photo", {})
        if photo_data is not None:
            self.photo = photo_data.get("url", "")
        else:
            self.photo = ""
        
        self.price = data.get("price", 0.0)
        self.discount = data.get("discount", None)
        self.currency = data.get("currency", "EUR")
        self.service_fee = data.get("service_fee", "")
        
        self.view_count = data.get("view_count", 0)
        self.favourite_count = data.get("favourite_count", 0)
        
        self.size_title = data.get("size_title", "")
        self.status = data.get("status", "")
        self.brand_title = data.get("brand_title", "")
        self.content_source = data.get('content_source', "catalog")
        
        self.promoted = data.get("promoted", False)
        
        user_data = data.get("user", {})
        if user_data is not None:
            self.user_id = user_data.get("id", -1)
            self.user_business = user_data.get("business", False)
            self.user_url = user_data.get("profile_url", "")
        else:
            self.user_id = -1
            self.user_business = False
            self.user_url = ""
        
        if photo_data is not None:
            high_res_data = photo_data.get("high_resolution")
            if high_res_data is not None:
                self.created_at = high_res_data.get("timestamp", None)
            else:
                self.created_at = None
        else:
            self.created_at = None
        
        self.section_names = section_names

    def __eq__(self, other):
        return self.id == other.id
    
    def to_dict(self):
        state = vars(self)
        column_name_section = "section"
        for section in self.section_names:
            state[column_name_section] = section
            column_name_section = f"sub_{column_name_section}"
        del state['section_names']
        return state
