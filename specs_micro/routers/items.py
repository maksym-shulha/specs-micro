import re

from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException, Request

from configs.db_config import collection
from laptop_specs_scraper import get_items_specs


router = APIRouter()


@router.get("/api/items/{item_id}")
async def read_item(item_id: str):
    """
    Retrieve item details by item ID.
    """
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")

        obj_id = ObjectId(item_id)

        item = await collection.find_one({'_id': obj_id})

        if item:
            item['_id'] = str(item['_id'])
            return item
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid item ID format: {e}")


@router.get("/api/selected")
async def read_items(ids: str = Query(..., description="List of item IDs")):
    """
    Retrieve item details by multiple item IDs.
    """
    id_list = [id.strip('"') for id in ids.strip("[]").replace(" ", "").split(",")]
    print(id_list)
    try:
        object_ids = [ObjectId(id) for id in id_list]

        items = await collection.find({'_id': {'$in': object_ids}}).to_list(length=len(object_ids))

        formatted_items = []
        for item in items:
            item['_id'] = str(item['_id'])
            formatted_items.append(item)

        return formatted_items

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid item ID format: {e}")


@router.get('/api/items', response_model=dict)
async def get_specs(request: Request,
                    producer: str = Query(None, description="Producer"),
                    series: str = Query(None, description="Series"),
                    cpu: str = Query(None, description="Cpu"),
                    gpu: str = Query(None, description="Gpu"),
                    displaysize: str = Query(None, description="Display size"),
                    page: int = Query(1, alias="page")):
    """
    Get items with specifications based on optional filter parameters.

    Parameters:
    - request (Request): The FastAPI request object.
    - producer (str, optional): Filter items by producer.
    - series (str, optional): Filter items by series.
    - cpu (str, optional): Filter items by CPU.
    - gpu (str, optional): Filter items by GPU.
    - displaysize (str, optional): Filter items by display size.
    - page (int, optional): Page number for paginated results. Default is 1.

    Returns:
    dict: A dictionary containing the paginated list of items with specifications and pagination details.

    Note:
    - Pagination is applied with a default page size of 5.
    - Items with specifications are retrieved based on the provided filter parameters.
    - Pagination details include total item count, current page, page size, total pages, and URLs for the previous and
    next pages.
    """
    page_size = 5
    skip = (page - 1) * page_size

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

    total_count = await collection.count_documents(filter_params)

    items_cursor = collection.find(filter_params).skip(skip).limit(page_size)
    items_list = await items_cursor.to_list(length=page_size)

    if not items_list:
        items_urls_lst = await get_items_specs(values_for_codes)
        if not items_urls_lst:
            return create_empty_response()

        total_count += await collection.count_documents({'url': {'$in': items_urls_lst}})
        items_cursor = collection.find({'url': {'$in': items_urls_lst}}).skip(skip).limit(page_size)
        items_list = await items_cursor.to_list(length=page_size)

    for item in items_list:
        item['_id'] = str(item['_id'])

    total_pages = -(-total_count // page_size)

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if skip + page_size < total_count else None

    krakend_base_url = "http://localhost:8080/laptops"
    request_url = str(request.url).replace(str(request.base_url) + 'api/items', krakend_base_url)

    prev_page_url = f"{request_url}{'&' if '?' in request_url else '?'}page={prev_page}" if prev_page else None
    next_page_url = f"{request_url}{'&' if '?' in request_url else '?'}page={next_page}" if next_page else None

    return {
        'total': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'prev_page': prev_page_url,
        'next_page': next_page_url,
        'items': items_list,
    }


def create_empty_response():
    return {'response': 'There are no items that satisfy search criteria'}
