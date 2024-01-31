import time

from crawl.requestor import get_response
from crawl.file_saving_manager import save_item
from crawl.processor import process, process_id
from crawl.ready_ids_manager import item_is_ready
from public.item_definer import ItemEnum


class Task:
    def __init__(self, item_enum: ItemEnum, url: str, params: dict = None):
        self.item_enum = item_enum
        self.url = url
        self.params = params
        self.raw_data = None
        self.time_stamp1 = 0.0
        self.time_stamp2 = 0.0
        self.time_stamp3 = 0.0

    def run(self):
        pass


class SingleItemTask(Task):
    def __init__(self, item_enum: ItemEnum, url: str, params: dict = None):
        super().__init__(item_enum, url, params)

    def run(self):
        self.time_stamp1 = time.time()

        self.raw_data = get_response(self.url, self.params)
        if not self.raw_data:
            return False

        self.time_stamp2 = time.time()

        # 如果已经保存过，则跳过
        processed_id = process_id(self.raw_data['id'])
        if item_is_ready(processed_id, self.item_enum):
            print(f'[tasks] {self.item_enum} {processed_id}已经保存过')
            self.time_stamp3 = time.time()
            return self.raw_data

        # 核心逻辑：处理、保存
        processed_data = process(self.raw_data, self.item_enum)
        save_item(processed_data, self.item_enum)

        self.time_stamp3 = time.time()
        return self.raw_data


class MultiItemTask(Task):
    def __init__(self, item_enum: ItemEnum, url: str, params: dict = None):
        super().__init__(item_enum, url, params)

    def run(self, bulk=True):
        self.time_stamp1 = time.time()

        self.raw_data = get_response(self.url, self.params)
        if not self.raw_data:
            return False

        self.time_stamp2 = time.time()

        already_saved_id_list = []

        if bulk:
            processed_data_list = []
            for item in self.raw_data['results']:
                # 如果已经保存过，则跳过
                processed_id = process_id(item['id'])
                if item_is_ready(processed_id, self.item_enum):
                    already_saved_id_list.append(processed_id)
                    continue

                # 核心逻辑：处理、保存
                processed_data = process(item, self.item_enum)
                save_item(processed_data, self.item_enum)
                processed_data_list.append(processed_data)
        else:
            for item in self.raw_data['results']:
                # 如果已经保存过，则跳过
                processed_id = process_id(item['id'])
                if item_is_ready(processed_id, self.item_enum):
                    already_saved_id_list.append(processed_id)
                    continue

                # 核心逻辑：处理、保存
                processed_data = process(item, self.item_enum)
                save_item(processed_data, self.item_enum)

        if already_saved_id_list:
            print(f'[tasks] {len(already_saved_id_list)}个{self.item_enum}已经保存过：{already_saved_id_list}')

        self.time_stamp3 = time.time()
        return self.raw_data

    def get_total_cnt(self):
        return self.raw_data['meta']['count']


class CurserMultiItemTask(MultiItemTask):
    def __init__(self, item_enum: ItemEnum, url: str, params: dict = None, start_cnt: int = 0):
        if 'cursor' not in params:
            params['cursor'] = '*'
        super().__init__(item_enum, url, params)
        self.start_cnt = start_cnt

    def get_next_start_cnt(self):
        return self.start_cnt + len(self.raw_data['results'])

    def get_next_cursor_task_dict(self):
        next_cursor = self.raw_data['meta']['next_cursor']
        if not next_cursor:
            return None
        next_params = self.params
        next_start_cnt = self.get_next_start_cnt()
        next_params['cursor'] = next_cursor
        return build_task_dict('cursor', self.item_enum, self.url, next_params, next_start_cnt)


def build_task_dict(task_type: str, item_enum: ItemEnum, url: str, params: dict = None, start_cnt: int = 0):
    return {
        'type': task_type,  # 'single' or 'multi' or 'cursor'
        'item_enum': item_enum.__str__(),
        'url': url,
        'params': params,
        'start_cnt': start_cnt
    }


def build_task(task_dict: dict):
    if task_dict['type'] == 'single':
        return SingleItemTask(ItemEnum[task_dict['item_enum']], task_dict['url'], task_dict['params'])
    elif task_dict['type'] == 'multi':
        return MultiItemTask(ItemEnum[task_dict['item_enum']], task_dict['url'], task_dict['params'])
    elif task_dict['type'] == 'cursor':
        return CurserMultiItemTask(ItemEnum[task_dict['item_enum']], task_dict['url'], task_dict['params'], task_dict['start_cnt'])
