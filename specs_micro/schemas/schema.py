def individual_serial(item) -> dict:
    return {
        'id': str(item['_id']),
        'producer': item['producer'],
        'series': item['series'],
        'model': item['model'],
        'price': item['price'],
        'specs': item['specs']
    }


def list_serial(items) -> list:
    return[individual_serial(item) for item in items]
