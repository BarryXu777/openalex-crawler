import os

from public.item_definer import ItemEnum

CACHES_PATH = 'caches'
CACHES_FILE_SAVING_PATH = f'{CACHES_PATH}/file_saving'
CACHES_READY_IDS_PATH = f'{CACHES_PATH}/ready_ids'
CACHES_TASK_QUEUE_PATH = f'{CACHES_PATH}/task_queue'
REPO_PATH = 'repo'


def REPO_ITEM_PATH(item_enum: ItemEnum):
    return f'{REPO_PATH}/{item_enum}s'


# 初始化
def init():
    dir_path_list = [
        CACHES_PATH,
        CACHES_FILE_SAVING_PATH,
        CACHES_READY_IDS_PATH,
        CACHES_TASK_QUEUE_PATH,
        REPO_PATH,
    ] + [REPO_ITEM_PATH(item_enum) for item_enum in ItemEnum]
    for path in dir_path_list:
        if not os.path.exists(path):
            os.makedirs(path)


init()
