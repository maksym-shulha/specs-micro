import re

from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException

from configs.db_config import collection
from laptop_specs_scraper import get_items_specs


router = APIRouter()


@router.get("/api/items/{item_id}")
def read_item(item_id: str):
    """
    Retrieve item details by item ID.
    """
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
    """
    Retrieve a list of items based on specified filter parameters.

    Note:
        If no items are found based on the specified filters, additional items
        may be fetched using external sources (e.g., `get_items_specs` function).
    """

    values_for_codes = []
    filter_params = {}
    if producer:
        values_for_codes.append(producer)
        filter_params["producer"] = producer
    if series:
        values_for_codes.append(series)
        filter_params["series"] = series
    if cpu:
        values_for_codes.append(cpu)
        cpu_pattern = re.escape(cpu) + '.*'
        filter_params["cpu"] = {'$regex': cpu_pattern}
    if gpu:
        values_for_codes.append(gpu)
        filter_params["gpu"] = gpu
    if displaysize:
        values_for_codes.append(displaysize)
        if displaysize == '9" - 12.5"':
            filter_params["displaysize"] = {'$gte': 9, '$lte': 12.9}
        elif displaysize == '13"':
            filter_params["displaysize"] = {'$gte': 13, '$lte': 13.9}
        elif displaysize == '14"':
            filter_params["displaysize"] = {'$gte': 14, '$lte': 14.9}
        elif displaysize == '15" - 15.6"':
            filter_params["displaysize"] = {'$gte': 15, '$lte': 15.9}
        elif displaysize == '16" - 17"':
            filter_params["displaysize"] = {'$gte': 16, '$lte': 17.9}
        elif displaysize == '18.4 " і більше':
            filter_params["displaysize"] = {'$gte': 18}

    items_list = list(collection.find(filter_params))

    if not items_list:
        items_urls_lst = get_items_specs(values_for_codes)
        if not items_urls_lst:
            return "There are no elements that satisfy the search criteria"
        items = collection.find({'url': {'$in': items_urls_lst}})
        items_list = list(items)

    for item in items_list:
        item['_id'] = str(item['_id'])

    return items_list
