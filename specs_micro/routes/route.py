from fastapi import APIRouter, Query
from configs.db_config import collection
from schemas.schema import list_serial

router = APIRouter()


@router.get('/api/items')
async def get_specs():
    specs = list_serial(collection.find())
    return specs


@router.get('/api/items/filter')
async def get_specs(
    producer: str = Query(None, description="Filter by producer"),
    series: str = Query(None, description="Filter by series"),
    model: str = Query(None, description="Filter by model"),
):

    query = {}
    if producer:
        query['producer'] = producer
    if series:
        query['series'] = series
    if model:
        query['model'] = model

    filtered_items = collection.find(query)

    specs = list_serial(filtered_items)
    return specs
