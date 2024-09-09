def compute_num_classes(section_categories : dict) -> dict:    
    return {k: len(v) for k, v in section_categories.items()}