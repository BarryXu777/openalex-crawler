# OpenAlex爬虫项目

## 项目介绍

本项目是一个OpenAlex文献数据集API的爬虫项目。

运行环境为python3.9，爬取结果以json格式保存到txt文件中。

本项目的优势在于：

1、在发生异步中断（SIGINT、SIGTERM）时，能够保存进度并在重新运行时继续。

2、在发生异常（同步）中断时，进度会保存，可以修复bug并重新运行，避免爬取发生不一致或无法恢复进度导致前功尽弃。

本项目的结构可为使用OpenAlex及其他各种API进行大规模数据爬取的需求提供参考。

本项目原用于BUAA软件系统分析与设计课程大作业regulus小组“学术星河”文献检索平台项目的千万级文献数据量爬取。

## OpenAlex介绍

OpenAlex是一个全球科研生态免费开源的索引服务，名字源自古代埃及亚历山大图书馆馆名，共收录了2.5亿部学术作品，以及它们的引文、作者、机构隶属关系等。

相关链接：

- [OpenAlex官网](https://openalex.org)
- [OpenAlex API文档](https://docs.openalex.org/)

## 如何运行

### get_entity_by_concept_runner.py

这个脚本可以将一次性爬取一个或多个领域下的所有work和author。

1.请在concept_id_list中加入需要爬取的work和author所属的领域concept id，已爬取的可以注释掉并标上领域名称

```python
concept_id_list = [
    # 'C115903868',  # Software Engineering
    # 'C108583219',  # Deep Learning
    # 'C3018397939',  # Open Source
    # 'C169590947',  # Compiler
    # 'C119823426',  # Computer-aided Design
    # 'C538814206',  # Computer-aided Engineering
    'C000000000',  # <领域名称>（本次需要执行的concept ID）
    'C111111111',  # <领域名称>（本次需要执行的concept ID）
]
```

2.直接运行这个脚本

```shell
python get_entity_by_concept_runner.py
```

3.如需要保存进度并中断，**请放心使用Ctrl+C（SIGINT）或`kill`命令（SIGTERM）**；如需继续，请再次运行。程序具有处理以上两种中断的能力

4.运行结束会看到`[crawler] 恭喜，爬取已完成，完成时间：<时间>`的输出，请将本次执行的concept id注释掉。接下来可以继续加入concept id进行下一轮执行，也可以执行其他脚本

### get_sample_entity_runner.py

这个脚本可以随机获取若干实体。

1.请在run_list加入要随机爬取的实体设置

'item_enum'字段的值为爬取实体枚举类型

'seed_range'字段的值为python range对象或整数组成的列表，range对象代表左闭右开的区间，如range(0, 20)代表[0, 20)的所有整数，通过这个字段可以设置随机种子，避免重复，详见openalex API文档https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/sample-entity-lists

```python
run_list = [
    # {'item_enum': ItemEnum.work, 'seed_range': range(0, 20)},
    {'item_enum': ItemEnum.author, 'seed_range': range(0, 20)},
]
```

2.剩余步骤同上个脚本

### get_all_entity_runner.py

这个脚本可以一次性爬取全部某种实体，如openalex中所有的concept、institution、source。

1.请在item_enum_list中加入要一次性爬取的实体类型枚举，已完成的可以注释掉。

```python
item_enum_list = [
    # ItemEnum.concept,
    # ItemEnum.institution,
    # ItemEnum.source
]
```

2.剩余步骤同上个脚本

### clear_runner.py

这个脚本可以清空任务队列，如果爬到一半，需要保存已爬取的数据并放弃当前任务去执行其他任务，可以执行这个脚本。

## 爬取结果的保存

爬取结果在目录`repo`中，运行时如果未发现这个目录则会自动创建。

默认一个文件中有1000条数据，如需改变这个配置，请修改`crawl\file_saving_manager.py`

```python
# 单个文件最大item数
MAX_ITEM_CNT = 1000
```

## 缓存文件解读

缓存文件位于`caches`目录中，会记录当前爬取进度等信息，请不要随意删除缓存文件。

目前的缓存文件都使用.txt或.json格式，方便阅读和异常情况的手动修改。

### 本地保存配置`caches\file_saving\data_cnt.json`

`caches\file_saving\data_cnt.json`中存储的是涉及当前`repo`目录下存储的爬取结果情况。

```json
{
  "work": {
    "file_cnt": 1319,
    "item_cnt": 353
  },
  "author": {
    "file_cnt": 666,
    "item_cnt": 290
  },
  "source": {
    "file_cnt": 250,
    "item_cnt": 409
  },
  "institution": {
    "file_cnt": 108,
    "item_cnt": 551
  },
  "concept": {
    "file_cnt": 66,
    "item_cnt": 73
  }
}
```

文件中"file_cnt"的值代表这个保存这个实体的最新文件序号，"item_cnt"的值代表这个最新文件中已存在的数据数量，默认一个文件中有1000条数据。

例如，

```json
  "work": {
    "file_cnt": 1319,
    "item_cnt": 353
  },
```

代表最新的文件时`repo\works\01319.txt`，这个文件中有353条数据。

### 已完成爬取的实体id`caches\ready_ids`

`caches\ready_ids`中存储的是已完成爬取的实体id，目的是为了避免重复保存影响性能和增大数据存储量。

### 任务队列配置`caches\task_queue`

`caches\task_queue`中存储的是任务队列配置。

#### 任务是什么

##### 任务类的继承关系

在`crawl\tasks.py`中定义了任务抽象类Task和它的子类SingleItemTask、MultiItemTask，以及MultiItemTask的子类CurserMultiItemTask，四个类的继承关系如下：

```
Task
  |--SingleItemTask
  |--MultiItemTask
        |--CurserMultiItemTask
```

- SingleItemTask对象表示爬取单个openalex实体的任务，如调用`https://api.openalex.org/works/W2100837269`
- MultiItemTask对象表示爬取多个openalex实体的任务，如调用`https://api.openalex.org/works`
- CurserMultiItemTask对象表示爬取多个openalex实体的任务且使用cursor进行分页持续爬取，如调用`https://api.openalex.org/works?per-page=200&cursor=*`，CurserMultiItemTask是当前程序实际需要使用的类。

##### 任务的执行

任务的`def run(self)`函数会执行任务，其中包括爬取一次数据、将数据保存到`repo`目录中两个动作。

##### CurserMultiItemTask任务产生下一分页爬取任务

CurserMultiItemTask的`def get_next_cursor_task_dict(self)`函数会根据`self.raw_data['meta']['next_cursor']`中得到的下一个cursor，产生下一分页的爬取任务字典，如果当前是最后一个分页，则这个函数返回None。

##### 任务与任务字典

`tasks.py`中`def build_task_dict`函数可以构造一个任务字典，方便加入任务队列但不立即执行这个任务。

`tasks.py`中`def build_task`函数可以根据任务字典构造一个任务对象，当需要从任务队列中取出任务并执行时需要调用，见`crawl\task_queue_manager.py`的`def fetch_task()`函数。

#### 任务队列是什么

任务队列是一个先进先出（FIFO）的队列，当需要执行新任务时，从队列首部取出任务，当需要加入新任务时，向队列尾部放入任务。

任务队列相关的脚本在`crawl\task_queue_manager.py`中。

当前共设置2个任务队列，`task_queue_0`和`task_queue_1`，优先执行序号较小的队列中的任务，直到序号较小的队列中无任务再执行序号较大的队列，任务队列数量可以如下配置，但当前程序只用到了第一个任务队列`task_queue_0`。

```
MAX_TASK_QUEUE_CNT = 2
```

#### 任务队列配置文件解读

`caches\task_queue\task_queue_0.txt`、`caches\task_queue\task_queue_1.txt`是以上两个任务队列的缓存文件，每行为一个json格式任务字典。

`caches\queue_config.json`是任务队列的配置文件，里面的内容可能为：

```json
{
  "task_queue_0_pos": 149,
  "task_queue_1_pos": 0
}
```

其含义是`task_queue_0`队列的首部从`caches\task_queue\task_queue_0.txt`第150行开始，即149行以前的任务已执行完成，下一个要执行的任务位于第150行；`task_queue_1`队列的首部从`caches\task_queue\task_queue_1.txt`第1行开始，没有已完成的任务，下一个要执行的任务位于第1行。

如果将要执行的任务对应的行数大于队列的总行数，意味着当前所有爬取任务已经完成。

如果遇到异常，可以查看`caches\queue_config.json`、`caches\task_queue\task_queue_0.txt`、`caches\task_queue\task_queue_1.txt`中的内容，找到对应出问题的任务和下一步要执行的任务，可以手动修改这些文件以按照我们的意图指定程序将要执行的任务。

## 最重要的说明

- 更多问题请阅读源码。
- 程序可以安全处理异步中断。
- 遇到异常，程序的缓存文件可以解决绝大多数问题。目前程序已经经过多轮爬取运行的迭代完善，很多bug已经解决。