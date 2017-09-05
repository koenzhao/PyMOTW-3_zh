**目标：使用SQL实现嵌入式关系型数据库**
sqlite3模块针对SQLite实现了兼容Python DB-API 2.0的接口，是一种进程内的关系型数据库。不同于MySQL，PostgreSQL,或者Oracle这一类使用分离型数据服务器的数据库系统，SQLite可以将数据库系统嵌入到应用内。它快速，灵活的特点，使它能适用于某些应用的原型和生产部署。
##创建一个数据库
SQLite的数据库是保存在文件系统中的一个文件。该库可以管理对文件的访问，包括当有多个使用者同时使用它时，能够对文件加锁防止文件损坏。当文件第一次被访问时，数据库就创建好了，应用负责管理数据库内的表定义或模式。
下面的示例在使用connect()之前查找数据库文件，以便于知道什么时候为新数据库创建模式。
```python
#sqlite3_createdb.py
import os
import sqlite3

db_filename = 'todo.db'

db_is_new = not os.path.exists(db_filename)

conn = sqlite3.connect(db_filename)

if db_is_new:
    print('Need to create schema')
else:
    print('Database exists, assume schema does, too.')

conn.close()
```
连续运行上面的脚本两次，如果数据库文件不存在的话，你会看到它自动创建了一个新的空文件。
```bash
$ ls *.db

ls: *.db: No such file or directory

$ python3 sqlite3_createdb.py

Need to create schema

$ ls *.db

todo.db

$ python3 sqlite3_createdb.py

Database exists, assume schema does, too.
```
创建好数据库文件后，下一步就是创建模式以便于我们在数据库中定义表。本节中接下来的示例都会使用同一个数据库模式来管理任务。具体内容如下两表所示。
The project Table

|Column|Type|Description|
|:-----|:--:|:----------|
|name|text|Project name|
|description|text|Long project description|
|deadline|data|Due date for the entrie project|

The task Table

|Column|Type|Description|
|:-----|:--:|:----------|
|id|number|Unique task identifier|
|priority|integer|Numerical priority, lower is more important|
|details|text|Full task details|
|status|text|Task status (one of 'new', 'pending', 'done', or 'canceled').|
|deadline|date|Due date for this task|
|completed|date|When the task was completed.|
|project|text|The name of the project for this task.|

使用数据定义语言(DDL,Data definition language)创建这些表：

```sql
-- todo_schema.sql
-- Schema for to-do application examples.

-- Projects are high-level activities made up of tasks
create table project (
    name        text primary key,
    description text,
    deadline    date
);

-- Tasks are steps that can be taken to complete a project
create table task (
    id           integer primary key autoincrement not null,
    priority     integer default 1,
    details      text,
    status       text,
    deadline     date,
    completed_on date,
    project      text not null references project(name)
);
```
Connection(连接)中的executescript()方法可以用来执行DDL指令，从而创建模式。

```python
# sqlite3_create_schema.py
import os
import sqlite3

db_filename = 'todo.db'
schema_filename = 'todo_schema.sql'

db_is_new = not os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if db_is_new:
        print('Creating schema')
        with open(schema_filename, 'rt') as f:
            schema = f.read()
        conn.executescript(schema)

        print('Inserting initial data')

        conn.executescript("""
        insert into project (name, description, deadline)
        values ('pymotw', 'Python Module of the Week',
                '2016-11-01');

        insert into task (details, status, deadline, project)
        values ('write about select', 'done', '2016-04-25',
                'pymotw');

        insert into task (details, status, deadline, project)
        values ('write about random', 'waiting', '2016-08-22',
                'pymotw');

        insert into task (details, status, deadline, project)
        values ('write about sqlite3', 'active', '2017-07-31',
                'pymotw');
        """)
    else:
        print('Database exists, assume schema does, too.')
```

在创建好表之后，我们使用几个insert语句创建了一个简单的项目和相关任务。使用sqlite3命令行程序可以查看数据库的内容。

```bash
$ rm -f todo.db
$ python3 sqlite3_create_schema.py

Creating schema
Inserting initial data

$ sqlite3 todo.db 'select * from task'

1|1|write about select|done|2016-04-25||pymotw
2|1|write about random|waiting|2016-08-22||pymotw
3|1|write about sqlite3|active|2017-07-31||pymotw
```

##检索数据
在Python程序内，我们可以通过数据库连接创建一个Cursor(游标）去检索保存在任务表中的数据。Cursor(游标)可以产生一致的数据视图，并且这也是与SQLite等事务数据库系统交互的主要方式。

```python
# sqlite3_select_tasks.py
import sqlite3

db_filename = 'todo.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    cursor.execute("""
    select id, priority, details, status, deadline from task
    where project = 'pymotw'
    """)

    for row in cursor.fetchall():
        task_id, priority, details, status, deadline = row
        print('{:2d} [{:d}] {:<25} [{:<8}] ({})'.format(
            task_id, priority, details, status, deadline))
```

查询过程主要分两步。第一步，通过运行cursor(游标)的execute()方法告诉数据库引擎需要收集哪些数据。然后使用fetchall()方法去检索收集的结果。它会返回一个元组序列，这个元组序列包括了select子句查询的内容。

```bash
$ python3 sqlite3_select_tasks.py

 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [waiting ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

我们可以使用fetchone()一次检索一个结果，或者使用fetchmany()在固定大小的情况下批量处理多个结果。

```python
# sqlite3_select_variations.py
import sqlite3

db_filename = 'todo.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    cursor.execute("""
    select name, description, deadline from project
    where name = 'pymotw'
    """)
    name, description, deadline = cursor.fetchone()

    print('Project details for {} ({})\n  due {}'.format(
        description, name, deadline))

    cursor.execute("""
    select id, priority, details, status, deadline from task
    where project = 'pymotw' order by deadline
    """)

    print('\nNext 5 tasks:')
    for row in cursor.fetchmany(5):
        task_id, priority, details, status, deadline = row
        print('{:2d} [{:d}] {:<25} [{:<8}] ({})'.format(
            task_id, priority, details, status, deadline))
```

我们传入fetchmany()的参数是指它要返回的最大项数。如果有效的项数比这个最大项数小，则返回序列中的项数比最大项数小。

```bash
$ python3 sqlite3_select_variations.py

Project details for Python Module of the Week (pymotw)
  due 2016-11-01

Next 5 tasks:
 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [waiting ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

##查找元数据





























