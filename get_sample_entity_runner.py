from crawl.crawler import Crawler, PER_PAGE
from crawl.task_queue_manager import clean_task_queues, add_task
from crawl.tasks import Task, build_task_dict
from public.item_definer import ItemEnum

run_list = [
    {'item_enum': ItemEnum.work, 'seed_range': range(0, 20)},
    {'item_enum': ItemEnum.author, 'seed_range': range(0, 20)},
]


def get_url(item_enum: ItemEnum):
    return f'https://api.openalex.org/{item_enum}s'


def get_params(item_enum: ItemEnum, seed: int):
    return {
        'sample': PER_PAGE,
        'per-page': PER_PAGE,
        'seed': seed
    }


def init_task():
    clean_task_queues()
    for run in run_list:
        for seed in run['seed_range']:
            add_task(0, build_task_dict(
                'multi',
                run['item_enum'],
                get_url(run['item_enum']),
                get_params(run['item_enum'], seed)
            ))


def after_task_run(task: Task):
    pass


if __name__ == '__main__':
    # clear_task_queues()  # 清空任务队列重新进行本次爬取，不会删除已爬取的内容
    crawler = Crawler(after_task_run, init_task)
    crawler.crawl()
