from crawl.crawler import PER_PAGE, Crawler
from crawl.task_queue_manager import add_task, clean_task_queues, clear_task_queues
from crawl.tasks import *


concept_id_list = [
    # 'C115903868',  # Software Engineering
    # 'C108583219',  # Deep Learning
    # 'C3018397939',  # Open Source
    # 'C169590947',  # Compiler
    # 'C119823426',  # Computer-aided Design
    # 'C538814206',  # Computer-aided Engineering
    # 'C154945302',  #Artificial Intelligence
    # 'C95444343',   # Cell biology
    # 'C19527891',  #Medical physics
    # 'C48824518',  #agricultural sciences
]

item_enum_list = [
    ItemEnum.work,
    ItemEnum.author
]


def get_url(item_enum: ItemEnum):
    return f'https://api.openalex.org/{item_enum}s'


def get_params(item_enum: ItemEnum, concept_id: str, cursor: str = '*'):
    if item_enum == ItemEnum.work:
        return {
            'filter': 'concepts.id:' + 'https://api.openalex.org/concepts/' + concept_id,
            'per-page': PER_PAGE,
            'cursor': cursor
        }
    if item_enum == ItemEnum.concept:
        return {
            'per-page': PER_PAGE,
            'cursor': cursor
        }
    else:
        return {
            'filter': 'x_concepts.id:' + 'https://api.openalex.org/concepts/' + concept_id,
            'per-page': PER_PAGE,
            'cursor': cursor
        }


def init_task():
    clean_task_queues()
    for concept_id in concept_id_list:
        for item_enum in item_enum_list:
            add_task(0, build_task_dict(
                'cursor',
                item_enum,
                get_url(item_enum),
                get_params(item_enum, concept_id, '*')
            ))


def after_task_run(task: Task):
    if isinstance(task, CurserMultiItemTask):
        add_task(0, task.get_next_cursor_task_dict())


if __name__ == '__main__':
    # clear_task_queues()  # 清空任务队列重新进行本次爬取，不会删除已爬取的内容
    crawler = Crawler(after_task_run, init_task)
    crawler.crawl()
