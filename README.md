# Laptop Specifications Microservice

This repository contains a FastAPI application for retrieving and updating laptop specifications. It consists of the following parts:

## 1. Endpoints:

### GET /api/items/{item_id}

**Description:** Retrieve item details by item ID.

**Parameters:**
- `item_id` (str): The ID of the item to retrieve.

**Returns:** 
- Item details as JSON if found, or a 404 error if the item is not found.

### GET /api/items

**Description:** Retrieve a list of items based on specified filter parameters.

**Parameters:**
- `producer` (str, optional): Producer filter.
- `series` (str, optional): Series filter.
- `cpu` (str, optional): CPU filter.
- `gpu` (str, optional): GPU filter.
- `displaysize` (str, optional): Display size filter.

**Returns:** 
- A list of items that match the specified filters. If no items are found, it may fetch additional items using external sources.

## 2. laptop_specs_scraper.py

This module contains functions for scraping laptop specifications from the 'brain.com.ua' website and storing them in MongoDB.

## 3. search_params_scraper.py

This module contains a script for scraping search parameters from the 'brain.com.ua' website and creating a mapping file ('brain_codes.json').

## 4. update_price.py

This module contains a script for updating laptop prices in the MongoDB collection by scraping the latest prices from their respective URLs.

