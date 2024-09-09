from torch.utils.data import DataLoader

import pandas as pd

from dataset import HierarchicalImageDataset
from preprocess import encode_labels, split_data
from utils import compute_num_classes
from config import batch_size, train_transform, val_transform, num_epochs, lr
from model import train_model, evaluate_model, predict

if __name__ == "__main__":
    df = pd.read_csv('C:\\Users\\charp\\Desktop\\Vinted\\data\\merged_results.csv')
    df = df.dropna(subset=['path_downloaded_photo', 'id'])
    
    always_include = ['id', 'url']
    section_columns = [col for col in df.columns if col.endswith('section')]
    columns_to_keep = always_include + section_columns
    df = df[columns_to_keep]
    
    df, section_categories = encode_labels(df)
    num_classes_dict = compute_num_classes(section_categories) 
    
    train_df, val_df, test_df = split_data(df)
    
    train_dataset = HierarchicalImageDataset(train_df, section_categories, transform=train_transform)
    val_dataset = HierarchicalImageDataset(val_df, section_categories, transform=val_transform)
    test_dataset = HierarchicalImageDataset(test_df, section_categories, transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = train_model(train_loader, val_loader, num_classes_dict, num_epochs=num_epochs, lr=lr)
    
    # test_loss = evaluate_model(model, test_loader)
    # print(f"Test Loss: {test_loss:.4f}")
    
    # url = 'https://example.com/votre_image.jpg'
    # predictions = predict(model, url, section_categories)
    # for section, prediction in predictions.items():
    #     print(f"{section}: {prediction}")