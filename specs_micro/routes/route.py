from fastapi import APIRouter, Query, HTTPException
from configs.db_config import collection
from schemas.schema import list_serial
from laptop_specs_scraper import get_items_specs
from bson import ObjectId


router = APIRouter()


@router.get("/items/{item_id}")
def read_item(item_id: str):
    try:
        obj_id = ObjectId(item_id)

        item = collection.find_one({'_id': obj_id})

        if item:
            item['_id'] = str(item['_id'])
            return item
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid item ID format: {e}")


@router.get('/api/items')
async def get_specs(filter: str = Query(None, description="Filter")):
    items_urls_lst = get_items_specs(filter)
    if not items_urls_lst:
        return "There are no elements that satisfy the search criteria"
    items = collection.find({'url': {'$in': items_urls_lst}})
    items_list = list(items)
    for item in items_list:
        item['_id'] = str(item['_id'])

    return items_list
