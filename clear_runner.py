from crawl.task_queue_manager import clear_task_queues

if __name__ == '__main__':
    clear_task_queues()  # 清空任务队列，用于重新进行本次爬取，不会删除已爬取的内容
