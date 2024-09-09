import torch
import torch.optim as optim
import torch.nn as nn
import torchvision.models as models

from PIL import Image

import pandas as pd
from tqdm import tqdm

from config import device, val_transform

class HierarchicalClassifier(nn.Module):
    def __init__(self, num_classes_dict):
        super(HierarchicalClassifier, self).__init__()
        
        self.resnet = models.resnet50(weights='DEFAULT')
        
        for param in self.resnet.parameters():
            param.requires_grad = False
            
        self.resnet.fc = nn.Identity() 
        
        self.fc_layers = nn.ModuleDict({
            'section': nn.Linear(2048, num_classes_dict['section']),
            'sub_section': nn.Linear(2048 + num_classes_dict['section'], num_classes_dict['sub_section']),
            'sub_sub_section': nn.Linear(2048 + num_classes_dict['section'] + num_classes_dict['sub_section'], num_classes_dict['sub_sub_section']),
            'sub_sub_sub_section': nn.Linear(2048 + num_classes_dict['section'] + num_classes_dict['sub_section'] + num_classes_dict['sub_sub_section'], num_classes_dict['sub_sub_sub_section']),
            'sub_sub_sub_sub_section': nn.Linear(2048 + num_classes_dict['section'] + num_classes_dict['sub_section'] + num_classes_dict['sub_sub_section'] + num_classes_dict['sub_sub_sub_section'], num_classes_dict['sub_sub_sub_sub_section']),
        })

    def forward(self, x):
        x = self.resnet(x)
        
        predictions = {}
        previous_outputs = []

        for level in ['section', 'sub_section', 'sub_sub_section', 'sub_sub_sub_section', 'sub_sub_sub_sub_section']:
            input_features = torch.cat([x] + previous_outputs, dim=1)
            output = self.fc_layers[level](input_features)
            predictions[level] = output
            previous_outputs.append(output)

        return predictions

def train_model(train_loader, val_loader, num_classes_dict, num_epochs=10, lr=0.001):
    model = HierarchicalClassifier(num_classes_dict).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()

    history_train_loss = []
    history_eval_loss = []

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        
        # Ajouter tqdm pour afficher la barre de progression pour l'entraînement
        for images, labels in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}', unit='batch'):
            images = images.to(device)
            labels = {key: val.to(device) for key, val in labels.items()}
            
            optimizer.zero_grad()
            outputs = model(images)
            
            loss = sum([criterion(outputs[key], labels[key]) for key in outputs.keys()])
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()

        train_loss /= len(train_loader)
        
        val_loss = evaluate_model(model, val_loader)
        
        history_train_loss.append(train_loss)
        history_eval_loss.append(val_loss)
        
        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}")
    
    results_df = pd.DataFrame({
        "Epoch": [i for i in range(num_epochs)],
        'Train Loss': history_train_loss, 
        'Validation Loss': history_eval_loss
    })
    results_df.to_csv('./training_results.csv', index=False)
    
    torch.save(model.state_dict(), './model.pth')
    
    return model

def evaluate_model(model, data_loader):
    model.eval()
    criterion = nn.BCEWithLogitsLoss()
    val_loss = 0.0
    
    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            labels = {key: val.to(device) for key, val in labels.items()}
            
            outputs = model(images)
            loss = sum([criterion(outputs[key], labels[key]) for key in outputs.keys()])
            
            val_loss += loss.item()

    val_loss /= len(data_loader)
    return val_loss


def predict(model, path, section_categories):
    image = Image.open(path).convert('RGB')
    
    image = val_transform(image).unsqueeze(0).to(device)
    
    model.eval()
    predictions = {}
    
    with torch.no_grad():
        outputs = model(image)
    
    for section, output in outputs.items():
        if isinstance(section_categories, dict):
            predicted_index = torch.sigmoid(output).squeeze().cpu().numpy() > 0.5
            predicted_labels = [category for idx, category in enumerate(section_categories[section]) if predicted_index[idx]]
            if len(predicted_labels) == 1:
                predictions[section] = predicted_labels[0]
            else:
                predictions[section] = 'Multiple Predictions'
        else:
            _, predicted_index = torch.max(output, 1)
            predicted_label = section_categories[section][predicted_index.item()]
            predictions[section] = predicted_label

    return predictions