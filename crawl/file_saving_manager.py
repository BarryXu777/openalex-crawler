import json

from public.path_manager import CACHES_FILE_SAVING_PATH, REPO_ITEM_PATH
from crawl.ready_ids_manager import add_ready_item
from public.file_utils import load_json, append_line, store_json
from public.item_definer import ItemEnum

# 单个文件最大item数
MAX_ITEM_CNT = 1000


# 路径配置
DATA_CNT_PATH = f'{CACHES_FILE_SAVING_PATH}/data_cnt.json'


def ITEM_SAVING_FILE_PATH(item_enum: ItemEnum):
    return f'{REPO_ITEM_PATH(item_enum)}/{data_cnt[item_enum.__str__()]["file_cnt"]:05d}.txt'


data_cnt = load_json(DATA_CNT_PATH, {
    # file_cnt: 当前文件最大编号, item_cnt: 最大编号文件已有的item数
    "work": {"file_cnt": 0, "item_cnt": 0},
    "author": {"file_cnt": 0, "item_cnt": 0},
    "source": {"file_cnt": 0, "item_cnt": 0},
    "institution": {"file_cnt": 0, "item_cnt": 0},
    "concept": {"file_cnt": 0, "item_cnt": 0}
})


def save_item(item: dict, item_enum: ItemEnum):
    # 更新data_cnt
    if data_cnt[item_enum.__str__()]['item_cnt'] >= MAX_ITEM_CNT or data_cnt[item_enum.__str__()]['file_cnt'] == 0:
        data_cnt[item_enum.__str__()]['file_cnt'] += 1
        data_cnt[item_enum.__str__()]['item_cnt'] = 0
    data_cnt[item_enum.__str__()]['item_cnt'] += 1
    store_json(DATA_CNT_PATH, data_cnt)

    # 保存item
    append_line(ITEM_SAVING_FILE_PATH(item_enum), json.dumps(item))

    # 将item加入到ready列表
    add_ready_item(item['id'], item_enum)
