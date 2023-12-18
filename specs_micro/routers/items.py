from fastapi import APIRouter, Query, HTTPException
from configs.db_config import collection
from laptop_specs_scraper import get_items_specs
from bson import ObjectId


router = APIRouter()


@router.get("/api/items/{item_id}")
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
async def get_specs(producer: str = Query(None, description="Producer"),
                    series: str = Query(None, description="Series"),
                    cpu: str = Query(None, description="Cpu"),
                    gpu: str = Query(None, description="Gpu"),
                    displaysize: str = Query(None, description="Display size")):

    filter_params = {}
    if producer:
        filter_params["producer"] = producer
    if series:
        filter_params["series"] = series
    if cpu:
        filter_params["cpu"] = cpu
    if gpu:
        filter_params["gpu"] = gpu
    if displaysize:
        filter_params["displaysize"] = displaysize

    results = list(collection.find(filter_params))

    if results:
        for item in results:
            item['_id'] = str(item['_id'])
        return results
    else:
        items_urls_lst = get_items_specs(filter_params)
        if not items_urls_lst:
            return "There are no elements that satisfy the search criteria"
        items = collection.find({'url': {'$in': items_urls_lst}})
        items_list = list(items)
        for item in items_list:
            item['_id'] = str(item['_id'])

        return items_list
