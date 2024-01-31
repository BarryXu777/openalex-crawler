from typing import Optional

from crawl.tasks import Task, build_task
from public.file_utils import load_json, load_json_list, store_json, append_json_line, store_json_list
from public.path_manager import CACHES_TASK_QUEUE_PATH

MAX_TASK_QUEUE_CNT = 2


QUEUE_CONFIG_PATH = f'{CACHES_TASK_QUEUE_PATH}/queue_config.json'


def TASK_QUEUE_FILE_PATH(queue: int):
    return f'{CACHES_TASK_QUEUE_PATH}/task_queue_{queue}.txt'


queue_config = load_json(QUEUE_CONFIG_PATH, {
    # pos: 下一个要执行的任务在队列中的位置
    f'task_queue_{i}_pos': 0 for i in range(MAX_TASK_QUEUE_CNT)
})
task_queues = [load_json_list(TASK_QUEUE_FILE_PATH(i)) for i in range(MAX_TASK_QUEUE_CNT)]


def get_task_queue_pos(queue: int):
    return queue_config[f'task_queue_{queue}_pos']


def set_task_queue_pos(queue: int, pos: int):
    queue_config[f'task_queue_{queue}_pos'] = pos


def push_task_queue_pos(queue: int):
    queue_config[f'task_queue_{queue}_pos'] += 1


def print_queue_task_cnt():
    print('[task queue manager] 队列任务完成情况：')
    for i in range(MAX_TASK_QUEUE_CNT):
        current = get_task_queue_pos(i)
        total = len(task_queues[i])
        print(f'[task queue manager] task_queue_{i}: {current}/{total}, 剩余{total - current}')


def add_task(queue: int, task_dict: dict):
    if not task_dict:
        return
    task_queues[queue].append(task_dict)
    append_json_line(TASK_QUEUE_FILE_PATH(queue), task_dict)


current_task_queue = -1


def fetch_task() -> Optional[Task]:
    for queue in range(MAX_TASK_QUEUE_CNT):
        if get_task_queue_pos(queue) < len(task_queues[queue]):
            global current_task_queue
            current_task_queue = queue
            task_dict = task_queues[queue][get_task_queue_pos(queue)]
            return build_task(task_dict)
    return None


def finish_task():
    push_task_queue_pos(current_task_queue)
    store_json(QUEUE_CONFIG_PATH, queue_config)


def clean_task_queues():
    """ 清理任务队列，将已完成的任务删除，不影响运行 """
    for i in range(MAX_TASK_QUEUE_CNT):
        task_queues[i] = [task_queues[i][j] for j in range(get_task_queue_pos(i), len(task_queues[i]))]
        store_json_list(TASK_QUEUE_FILE_PATH(i), task_queues[i])
        set_task_queue_pos(i, 0)
    store_json(QUEUE_CONFIG_PATH, queue_config)


def clear_task_queues():
    """ 清空任务队列，重新运行，但不会删除已爬取的内容 """
    for i in range(MAX_TASK_QUEUE_CNT):
        store_json_list(TASK_QUEUE_FILE_PATH(i), [])
        set_task_queue_pos(i, 0)
    store_json(QUEUE_CONFIG_PATH, queue_config)
