class Item:
    def __init__(self, data):
        print(data)
        self.id = data.get("id", None)
        
        self.title = data.get("title", "")
        self.url = data.get("url", "")
        self.photo = data.get("photo", {}).get("url", "")
        
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
        
        self.user_id = data.get("user", {}).get("id", 0)
        self.user_business = data.get("user", {}).get("business", False)
        self.user_url = data.get("user", {}).get("profile_url", "")
        
        self.created_at = data.get("photo", {}).get("high_resolution", {}).get("timestamp", None)

    def __eq__(self, other):
        return self.id == other.id
