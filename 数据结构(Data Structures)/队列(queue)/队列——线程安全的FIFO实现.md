#队列——线程安全的FIFO实现
**目标：提供一种线程安全的FIFO实现**
queue模块提供了一种适用于多线程编程的先进先出(FIFO)数据结构。它能够在生产者和消费者线程之间安全地传递消息或其他数据。它会为调用者处理锁定，所以多个线程之间可以安全地处理同一个Queue实例。Queue的大小(其中包含元素的个数)可能会受限，已限制内存使用或处理。
##基本的FIFO队列
Queue类实现了一个基本的先进先出容器。使用put()可以将元素添加到序列的一端，使用get()可以从序列的另一端移除元素。
```python
# queue_fifo.py
import queue

q = queue.Queue()

for i in range(5):
    q.put(i)

while not q.empty():
    print(q.get(), end=' ')
print()
```
上面的例子使用一个单线程程序说明了，队列中的元素在移除的时候的顺序和插入时的顺序是一致的。
```bash
$ python3 queue_fifo.py

0 1 2 3 4
```
##后进先出队列
与FIFO队列实现相反，LIFO队列遵循后进先出的顺序（通常作为栈数据结构访问）。
```python
# queue_lifo.py
import queue

q = queue.LifoQueue()

for i in range(5):
    q.put(i)

while not q.empty():
    print(q.get(), end=' ')
print()
```
最后一个放进去的元素会最先被get()取出来。
```bash
$ python3 queue_lifo.py

4 3 2 1 0
```
##优先队列
有时候，队列中元素的处理顺序需要根据这些元素的特征，而不是仅仅依靠它们创建或添加到队列中的顺序。举个例子，财务部门的打印工作可能要优先于开发人员的代码清单。PriorityQueue使用队列内容的有序顺序来决定使用哪一个元素。
```python
# queue_priority.py
import functools
import queue
import threading


@functools.total_ordering
class Job:

    def __init__(self, priority, description):
        self.priority = priority
        self.description = description
        print('New job:', description)
        return

    def __eq__(self, other):
        try:
            return self.priority == other.priority
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        try:
            return self.priority < other.priority
        except AttributeError:
            return NotImplemented


q = queue.PriorityQueue()

q.put(Job(3, 'Mid-level job'))
q.put(Job(10, 'Low-level job'))
q.put(Job(1, 'Important job'))


def process_job(q):
    while True:
        next_job = q.get()
        print('Processing job:', next_job.description)
        q.task_done()


workers = [
    threading.Thread(target=process_job, args=(q,)),
    threading.Thread(target=process_job, args=(q,)),
]
for w in workers:
    w.setDaemon(True)
    w.start()

q.join()
```
这个例子使用多线程消耗工作，在调用get()时获取到队列中元素的优先级属性，并依据该属性处理队列中的元素。在消费者线程中，处理添加到队列中元素的顺序取决与线程上下文的切换。
```bash
$ python3 queue_priority.py

New job: Mid-level job
New job: Low-level job
New job: Important job
Processing job: Important job
Processing job: Mid-level job
Processing job: Low-level job
```
##构建一个多线程播客客户端
本小节中的播客客户端程序源码展示了如何在多线程中使用线程。这段程序会读取一个或多个RSS订阅源，并将每个订阅源最新的5张专辑的附件加入队列准备下载，然后使用多线程并行处理这几个下载。虽然从产品使用的角度来看，本例的客户端没有设定足够多的错误处理，但基本的框架实现能说明我们对queue模块的使用。
首先，我们需要建立一些操作参数。通常，这些参数由用户输入（例如，性能或数据库）。本例中线程的数量取决于用户的输入值，并且还需要一张要去获取信息的URL列表。
```python
# fetch_podcasts.py
from queue import Queue
import threading
import time
import urllib
from urllib.parse import urlparse

import feedparser

# Set up some global variables
num_fetch_threads = 2
enclosure_queue = Queue()

# A real app wouldn't use hard-coded data...
feed_urls = [
    'http://talkpython.fm/episodes/rss',
]


def message(s):
    print('{}: {}'.format(threading.current_thread().name, s))
```
download_enclosures()函数将在工作线程中运行，它会通过urllib处理下载的内容。
```python
def download_enclosures(q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and exit only when
    the main thread ends.
    """
    while True:
        message('looking for the next enclosure')
        url = q.get()
        filename = url.rpartition('/')[-1]
        message('downloading {}'.format(filename))
        response = urllib.request.urlopen(url)
        data = response.read()
        # Save the downloaded file to the current directory
        message('writing to {}'.format(filename))
        with open(filename, 'wb') as outfile:
            outfile.write(data)
        q.task_done()
```
当我们有了目标函数后，工作线程就可以启动了。当download_enclosures()运行语句url = q.get()时，它会阻塞线程直到队列返回东西给线程。这意味着在队列中没有任何东西的时候，启动线程也是安全的。
```python
# Set up some threads to fetch the enclosures
for i in range(num_fetch_threads):
    worker = threading.Thread(
        target=download_enclosures,
        args=(enclosure_queue,),
        name='worker-{}'.format(i),
    )
    worker.setDaemon(True)
    worker.start()
```
下一步是运用feedparser模块检索订阅源内容，并排列好附件的URL。当第一个URL被添加到队列中时，某一个工作线程就会将这个URL取出来并开始下载它。循环会连续地添加项目直到订阅源被耗尽，而工作线程会从队列中取出URL并下载它们。
```python
# Download the feed(s) and put the enclosure URLs into
# the queue.
for url in feed_urls:
    response = feedparser.parse(url, agent='fetch_podcasts.py')
    for entry in response['entries'][:5]:
        for enclosure in entry.get('enclosures', []):
            parsed_url = urlparse(enclosure['url'])
            message('queuing {}'.format(
                parsed_url.path.rpartition('/')[-1]))
            enclosure_queue.put(enclosure['url'])
```
剩下还需要做的事情就是使用join()去等待队列被取完变成空。
```python
# Now wait for the queue to be empty, indicating that we have
# processed all of the downloads.
message('*** main thread waiting')
enclosure_queue.join()
message('*** done')
```
运行脚本会输入如下相似的信息：
```python
$ python3 fetch_podcasts.py

worker-0: looking for the next enclosure
worker-1: looking for the next enclosure
MainThread: queuing turbogears-and-the-future-of-python-web-frameworks.mp3
MainThread: queuing continuum-scientific-python-and-the-business-of-open-source.mp3
MainThread: queuing openstack-cloud-computing-built-on-python.mp3
MainThread: queuing pypy.js-pypy-python-in-your-browser.mp3
MainThread: queuing machine-learning-with-python-and-scikit-learn.mp3
MainThread: *** main thread waiting
worker-0: downloading turbogears-and-the-future-of-python-web-frameworks.mp3
worker-1: downloading continuum-scientific-python-and-the-business-of-open-source.mp3
worker-0: looking for the next enclosure
worker-0: downloading openstack-cloud-computing-built-on-python.mp3
worker-1: looking for the next enclosure
worker-1: downloading pypy.js-pypy-python-in-your-browser.mp3
worker-0: looking for the next enclosure
worker-0: downloading machine-learning-with-python-and-scikit-learn.mp3
worker-1: looking for the next enclosure
worker-0: looking for the next enclosure
MainThread: *** done
```
实际输出会因为RSS订阅源实时内容不同而不同。
















