from crawl.crawler import PER_PAGE, Crawler
from crawl.task_queue_manager import clean_task_queues, add_task
from crawl.tasks import build_task_dict, Task, CurserMultiItemTask
from public.item_definer import ItemEnum

# 当前已全部爬取完成，此脚本的意义已达到，可以不用再次运行
item_enum_list = [
    ItemEnum.concept,
    # ItemEnum.institution,
    # ItemEnum.source
]


def get_url(item_enum: ItemEnum):
    return f'https://api.openalex.org/{item_enum}s'


def init_task():
    clean_task_queues()
    for item_enum in item_enum_list:
        add_task(0, build_task_dict(
            'cursor',
            item_enum,
            get_url(item_enum),
            {
                'per-page': PER_PAGE,
                'cursor': '*'
            }
        ))


def after_task_run(task: Task):
    if isinstance(task, CurserMultiItemTask):
        add_task(0, task.get_next_cursor_task_dict())


if __name__ == '__main__':
    # clear_task_queues()  # 清空任务队列重新进行本次爬取，不会删除已爬取的内容
    crawler = Crawler(after_task_run, init_task)
    crawler.crawl()
