from public.file_utils import load_txt, append_line
from public.item_definer import ItemEnum
from public.path_manager import CACHES_READY_IDS_PATH


def READY_IDS_FILE_PATH(item_enum: ItemEnum):
    return f'{CACHES_READY_IDS_PATH}/ready_{item_enum}_ids.txt'


ready_ids = {
    ItemEnum.work: [],
    ItemEnum.author: [],
    ItemEnum.source: [],
    ItemEnum.institution: [],
    ItemEnum.concept: [],
}
for item_enum in ItemEnum:
    ready_ids[item_enum] = load_txt(READY_IDS_FILE_PATH(item_enum))


def print_ready_item_cnt():
    print('[ready ids manager] 当前已爬取并保存：')
    for item_enum in ItemEnum:
        print(f'[ready ids manager] {item_enum:15}: {len(ready_ids[item_enum])}')


def get_ready_item_cnt(item_enum: ItemEnum):
    return len(ready_ids[item_enum])


def item_is_ready(item_id: str, item_enum: ItemEnum) -> bool:
    return item_id in ready_ids[item_enum]


def add_ready_item(item_id: str, item_enum: ItemEnum):
    ready_ids[item_enum].append(item_id)
    append_line(READY_IDS_FILE_PATH(item_enum), item_id)
