import re

from public.item_definer import ItemEnum


def process(item: dict, item_enum: ItemEnum):
    item = process_dict(item)
    if item_enum == ItemEnum.work:
        item['abstract'] = reconstruct_abstract(item['abstract_inverted_index'])
        del item['abstract_inverted_index']
    return item


def process_dict(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = process_dict(value)
    elif isinstance(data, list):
        data = [process_dict(item) for item in data]
    elif isinstance(data, str):
        data = process_id(data)
    return data


def process_id(url_id: str):
    match = re.match(r'https://openalex.org/([a-zA-Z]\d{2,})', url_id)
    if match:
        return match.group(1)
    else:
        return url_id


def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return None
    word_array = [''] * (max(max(positions, default=-1) for positions in inverted_index.values()) + 1)
    for word, indexes in inverted_index.items():
        for index in indexes:
            word_array[index] = word
    reconstructed_article = ' '.join(word_array)
    if not reconstructed_article:
        return None
    return reconstructed_article
