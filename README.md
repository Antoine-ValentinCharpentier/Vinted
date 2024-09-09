# Vinted

## Overview

This project aims to be a tool that analyzes products sold on Vinted to determine if the selling price of new items is lower than the predicted price. If it is, it may be a good opportunity to make a purchase and get a good deal.

However, it is common for items to be listed in the wrong categories. Therefore, it would be useful to develop a model that analyzes the image of the item to determine its correct category (for example, a pair of pants listed under a T-shirt category should still be identified as pants).

The project consists of the following steps:
1. Scraping data from Vinted
2. Detecting the correct category of the item
3. Predicting the price

The current project only handles the first two parts.

## Setup

```bash
git clone git@github.com:Antoine-ValentinCharpentier/Vinted.git

cd vinted

conda create -n vinted python=3.12.4

conda activate vinted

pip install -r requirements.txt
```

## Usage

### Data Collection

First, you need to collect the relevant data from Vinted that you want to analyze. You can use the `main.ipynb` notebook located in the `scrapper` folder for this purpose.

You have two options:
1. If you want to scrape a single catalog, go to Vinted and navigate to the desired catalog. Then, copy the URL of the webpage and paste it into the first parameter of the `vinted.search(...)` function in the notebook. You can adjust the number of items per page and specify the starting and ending pages.
2. If you want to collect data from multiple catalogs, you can use the `vinted.search_all(...)` function. Note that you can exclude catalogs you don't want to scrape by listing their names in the `excludes_catalogs_names` attribute.

To train the models for steps 2 and 3, you'll need to collect multiple pages from each catalog, so it's recommended to use the `vinted.search_all(...)` function.

All collected data will be saved in the `data` folder, with a CSV file for each catalog and a subfolder named `photos` containing all the images of each item. This is important because the images may no longer be available later.

### Classification

Once you've collected the data, you'll need to train the image classification model to determine the correct category for each item.

First, merge the previously extracted data. You can do this by running all the cells in the `main.ipynb` notebook located in the `data_preparation` folder.

Next, you'll need to obtain the model by training it. You can do this by using the `main.py` script located in the `classification` folder. This script will generate the model weights and save them in the `model.pth` file within the `classification` folder.

This model can later be used to predict the category of each item (code coming soon).

### Regression

Not yet implemented...
