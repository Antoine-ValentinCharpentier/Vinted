import pandas as pd
from torch.utils.data import Dataset
from PIL import Image

class HierarchicalImageDataset(Dataset):
    def __init__(self, dataframe, section_categories, transform=None):
        self.dataframe = dataframe
        self.section_categories = section_categories
        self.transform = transform

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        image = Image.open(row['path_downloaded_photo']).convert('RGB')

        if self.transform:
            image = self.transform(image)

        labels = {}
        for section, categories in self.section_categories.items():
            labels[section] = row[[f'{section}_{cat}' for cat in categories]].values.astype('float64')

        return image, labels