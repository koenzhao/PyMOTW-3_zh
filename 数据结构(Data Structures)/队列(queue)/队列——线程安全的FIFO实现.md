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





















