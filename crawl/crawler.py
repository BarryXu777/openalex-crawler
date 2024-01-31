import time
from urllib.parse import urlencode

from crawl.interruption_manager import interrupted
from crawl.ready_ids_manager import print_ready_item_cnt
from crawl.task_queue_manager import print_queue_task_cnt, fetch_task, finish_task
from crawl.tasks import Task, SingleItemTask, CurserMultiItemTask, MultiItemTask

PER_PAGE = 200


def join_url(url, params):
    return f"{url}?{urlencode(params)}" if params else url


def print_task_start_info(task: Task):
    print(f"[crawler] "
          f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
          f"开始执行 {task.__class__.__name__}:{task.item_enum} {join_url(task.url, task.params)}")


def print_task_finished_info(task: Task):
    if isinstance(task, SingleItemTask):
        print(f"[crawler] "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"执行完成，爬取耗时{task.time_stamp2 - task.time_stamp1}s，处理耗时{task.time_stamp3 - task.time_stamp2}s")
    elif isinstance(task, CurserMultiItemTask):
        readied_cnt = task.get_next_start_cnt()
        total_cnt = task.get_total_cnt()
        estimated_time = (task.time_stamp3 - task.time_stamp1) * (total_cnt - readied_cnt) / PER_PAGE * 1.125
        print(f"[crawler] "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"执行完成，爬取耗时{task.time_stamp2 - task.time_stamp1}s，处理耗时{task.time_stamp3 - task.time_stamp2}s，"
              f"分页进度{readied_cnt}/{total_cnt}({(readied_cnt/total_cnt if total_cnt != 0 else 1):.2%})，"
              f"完成所有分页预计还需{time.strftime('%j天%H:%M:%S', time.gmtime(estimated_time))}，"
              f"队列中仅有此任务的情况下预计完成时间{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + estimated_time))}")
    elif isinstance(task, MultiItemTask):
        print(f"[crawler] "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"执行完成，爬取耗时{task.time_stamp2 - task.time_stamp1}s，处理耗时{task.time_stamp3 - task.time_stamp2}s，")


class Crawler:

    def __init__(self, after_task_run: callable, init_task: callable):
        self.after_task_run = after_task_run
        self.init_task = init_task

    def crawl(self):
        print('[crawler] 程序开始！当前时间：', time.strftime("%Y-%m-%d %H:%M:%S"))
        print_ready_item_cnt()
        print_queue_task_cnt()
        print('[crawler] 如需要保存进度并中断，请放心使用Ctrl+C或kill命令，程序具有处理中断的能力')
        print('[crawler] 如需要放弃所有进度，请删除caches和repo目录，已爬取内容将丢失')
        print('[crawler] 程序的缓存信息可以解决绝大多数异常中断的问题，每爬取一个数据都将记录以尽可能保证数据一致，遇到错误一般可以修改缓存信息或修改代码来恢复，无需重新爬取')
        if not fetch_task():
            wait_time = 5
            print(f'[crawler] 任务队列为空，首次开始爬取，等待{wait_time}秒后开始，如不需要重新开始请及时中断')
            time.sleep(wait_time)
            if interrupted():
                print('[crawler] 程序已中断，程序仍保持空任务队列状态')
                exit(0)
            print('[crawler] 执行init()函数初始化任务队列')
            self.init_task()
        while True:
            task = fetch_task()
            if task is None:
                print(f'[crawler] 恭喜，爬取已完成，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')
                print('[crawler] Hooray!')
                break
            if interrupted():
                print('[crawler] 程序遇到异步中断退出，下次运行将从当前进度继续')
                break
            print_task_start_info(task)
            result = task.run()
            if not result:
                if interrupted():
                    print('[crawler] 爬取时遇到异步中断退出，下次运行将从当前进度继续')
                else:
                    print('[crawler] 爬取时遇到错误，程序退出')
                break
            print_task_finished_info(task)
            self.after_task_run(task)
            finish_task()
        print_ready_item_cnt()
        print_queue_task_cnt()
        exit(0)
