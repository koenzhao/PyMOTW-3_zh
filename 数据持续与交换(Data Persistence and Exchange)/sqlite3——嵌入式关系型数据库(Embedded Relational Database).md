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
        task_id, priority, details, s
        tatus, deadline = row
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
在DB-API 2.0规范里有说，在调用execute()之后，cursor应该将其description属性保存fetch方法返回的数据信息。在API规范中，description是一个包含了列名，类型，显示大小，内部大小，精度，比例以及表示是否接受空值的标志的一个元组序列。

```python
# sqlite3_cursor_description.py
import sqlite3

db_filename = 'todo.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    cursor.execute("""
    select * from task where project = 'pymotw'
    """)

    print('Task table has these columns:')
    for colinfo in cursor.description:
        print(colinfo)
```

因为sqlite3不会对插入数据库的数据进行强制类型转换或大小限制，所以只有列名。

```bash
$ python3 sqlite3_cursor_description.py

Task table has these columns:
('id', None, None, None, None, None, None)
('priority', None, None, None, None, None, None)
('details', None, None, None, None, None, None)
('status', None, None, None, None, None, None)
('deadline', None, None, None, None, None, None)
('completed_on', None, None, None, None, None, None)
('project', None, None, None, None, None, None)
```

##行对象
默认情况下，fetch方法返回数据库中的值(row)是一个元组。调用者应该知道查询中列的顺序，并从元组中提取出各个值。当查询中值的数量增加，或提取数据的代码在库中扩展时，通常使用一个对象和列名来访问值的处理方式会更加方便。这样的话，当我们编辑新的查询时，元组内容的数量和顺序都可以修改，但与查询结果相关的代码基本不用改动。
Connection对象具有一个row_factory属性，允许通过调用代码来控制创建对象的类型，以表示查询结果中的每一行。sqlite3中还包括一个可以作为row factory(行工厂)的Row类。我们可以通过Row对象，使用列索引或列名去访问指定列的值。

```python
# sqlite3_row_factory.py
import sqlite3

db_filename = 'todo.db'

with sqlite3.connect(db_filename) as conn:
    # Change the row factory to use Row
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
    select name, description, deadline from project
    where name = 'pymotw'
    """)
    name, description, deadline = cursor.fetchone()

    print('Project details for {} ({})\n  due {}'.format(
        description, name, deadline))

    cursor.execute("""
    select id, priority, status, deadline, details from task
    where project = 'pymotw' order by deadline
    """)

    print('\nNext 5 tasks:')
    for row in cursor.fetchmany(5):
        print('{:2d} [{:d}] {:<25} [{:<8}] ({})'.format(
            row['id'], row['priority'], row['details'],
            row['status'], row['deadline'],
        ))
```

sqlite3_row_factory.py是sqlite3_select_variations.py中的例子，只是用Row对象而不是元组。项目表中的行仍然是通过访问列值的位置来打印的，但打印task的时候我们改用关键字查找，所以后面列的顺序被更改了也没有关系。

```bash
$ python3 sqlite3_row_factory.py

Project details for Python Module of the Week (pymotw)
  due 2016-11-01

Next 5 tasks:
 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [waiting ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

##使用变量查询
如果查询定义为字面量字符串嵌入到程序中，这种查询方式是不灵活的。举个例子，当另一个项目也添加到数据库中，想要显示前5个任务的话就应该更新，以处理其中的某一个项目。一种更灵活的方式是，建立一个SQL语句，在Python中结合相应的值得到所需的查询。然而，以这种方式建立一个查询语句是危险的，我们应该避免这种方式。如果你不能完全正确地转义查询语句中变量部分的特殊字符，则会导致SQL解析出错，或还有一种更糟的情况，有一类安全漏洞称为数据库注入，它允许入侵者在数据库中执行任意SQL语句。
在查询中使用动态值的正确做法是，利用随SQL指令一起传入execute()的宿主变量。当SQL语句执行时，SQL语句中的占位符会被替换为宿主变量的值。在SQL语句解析之前，使用宿主变量而不是插入任意的值，可以避免注入式攻击，因为不可靠值没有机会去影响SQL的解析。SQLite支持两种形式带占位符的查询，分别是位置参数和命名参数。
###位置参数
一个问号(?)代表一个位置参数，将作为元组的一个成员传入execute()。

```python
# sqlite3_argument_positional.py
import sqlite3
import sys

db_filename = 'todo.db'
project_name = sys.argv[1]

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    query = """
    select id, priority, details, status, deadline from task
    where project = ?
    """

    cursor.execute(query, (project_name,))

    for row in cursor.fetchall():
        task_id, priority, details, status, deadline = row
        print('{:2d} [{:d}] {:<25} [{:<8}] ({})'.format(
            task_id, priority, details, status, deadline))
```

命令行参数可以作为一个位置参数安全地传递给查询，其他恶意数据就没有机会能够破坏数据库。

```bash
$ python3 sqlite3_argument_positional.py pymotw

 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [waiting ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

###命名参数
当查询需要许多参数，或在查询中某些参数多次重复出现时，我们应当使用命名参数。命名参数需要带一个:前缀（如，:param_name）。

```python
# sqlite3_argument_named.py
import sqlite3
import sys

db_filename = 'todo.db'
project_name = sys.argv[1]

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    query = """
    select id, priority, details, status, deadline from task
    where project = :project_name
    order by deadline, priority
    """

    cursor.execute(query, {'project_name': project_name})

    for row in cursor.fetchall():
        task_id, priority, details, status, deadline = row
        print('{:2d} [{:d}] {:<25} [{:<8}] ({})'.format(
            task_id, priority, details, status, deadline))
```

位置参数和命名参数都不需要加引号或转义，因为查询解析器会对他们做特殊处理。

```bash
$ python3 sqlite3_argument_named.py pymotw

 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [waiting ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

查询参数可以用于select,insert和update语句，查询中字面量出现的地方都可以放置查询参数。

```python
# sqlite3_argument_update.py

import sqlite3
import sys

db_filename = 'todo.db'
id = int(sys.argv[1])
status = sys.argv[2]

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()
    query = "update task set status = :status where id = :id"
    cursor.execute(query, {'status': status, 'id': id})
```

上面程序中的update语句使用了两个命名参数。其中id是用来定位所要修改的行，status是要写入表中的值。

```bash
$ python3 sqlite3_argument_update.py 2 done
$ python3 sqlite3_argument_named.py pymotw

 1 [1] write about select        [done    ] (2016-04-25)
 2 [1] write about random        [done    ] (2016-08-22)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

##批量加载
如果要对一个很大的数据集执行同一条SQL指令，可以使用executemany()。这样对加载数据是十分有用的，因为这样可以避免在Python中使用循环处理输入，让底层库对循环处理进行优化。下面这个程序示例通过csv模块从一个逗号分隔值(comma-separated value file)文件中读取出一个任务列表，然后加载到数据库中。

```python
# sqlite3_load_csv.py
import csv
import sqlite3
import sys

db_filename = 'todo.db'
data_filename = sys.argv[1]

SQL = """
insert into task (details, priority, status, deadline, project)
values (:details, :priority, 'active', :deadline, :project)
"""

with open(data_filename, 'rt') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()
        cursor.executemany(SQL, csv_reader)
```

样本数据文件tasks.csv内容如下：

```csv
deadline,project,priority,details
2016-11-30,pymotw,2,"finish reviewing markup"
2016-08-20,pymotw,2,"revise chapter intros"
2016-11-01,pymotw,1,"subtitle"
```

运行程序：

```python
$ python3 sqlite3_load_csv.py tasks.csv
$ python3 sqlite3_argument_named.py pymotw

 1 [1] write about select        [done    ] (2016-04-25)
 5 [2] revise chapter intros     [active  ] (2016-08-20)
 2 [1] write about random        [done    ] (2016-08-22)
 6 [1] subtitle                  [active  ] (2016-11-01)
 4 [2] finish reviewing markup   [active  ] (2016-11-30)
 3 [1] write about sqlite3       [active  ] (2017-07-31)
```

##定义新列类型
SQLite对整数，浮点数，文本列具备原生的支持。sqlite3会自动将这些类型的数据从Python的表示转换到一种数据库存储的值，并且可以根据需要进行反向转换。数据库中的整数会根据数值的大小加载为整型(int)或长整型(long)。文本信息会被保存并检索成一个字符串，除非Connection的text_factory属性被修改了。
尽管SQLite内部只支持几种数据类型，但是sqlite3支持了自定义类型的功能，所以在Python应用中可以存储任意数据类型列。除了默认支持自动转换的那些类型，其他数据类型的转换可以在数据库连接中使用detect_types标志打开。如果定义表时，列使用所要求的类型来声明，可以使用PARSE_DECLTYPES。
```python
# sqlite3_date_types.py
import sqlite3
import sys

db_filename = 'todo.db'

sql = "select id, details, deadline from task"


def show_deadline(conn):
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    for col in ['id', 'details', 'deadline']:
        print('  {:<8}  {!r:<26} {}'.format(
            col, row[col], type(row[col])))
    return


print('Without type detection:')
with sqlite3.connect(db_filename) as conn:
    show_deadline(conn)

print('\nWith type detection:')
with sqlite3.connect(db_filename,
                     detect_types=sqlite3.PARSE_DECLTYPES,
                     ) as conn:
    show_deadline(conn)
```
sqlite3提供了针对日期及时间戳的转换器，它使用datetime模块中的date类和datetime类表示Python中的值。日期相关的转换器都会在类型检测的时候自动打开。
```bash
$ python3 sqlite3_date_types.py

Without type detection:
  id        1                          <class 'int'>
  details   'write about select'       <class 'str'>
  deadline  '2016-04-25'               <class 'str'>

With type detection:
  id        1                          <class 'int'>
  details   'write about select'       <class 'str'>
  deadline  datetime.date(2016, 4, 25) <class 'datetime.date'>
```
定义一个新类型需要先注册两个函数。Adapter(适配器)会接收一个Python对象然后返回一个可以存储在数据库中的字符串。Converter(转换器)接收一个数据库的字符串然后返回一个Python对象。可以通过register_adapter()定义一个适配器函数，register_converter()定义一个转换器函数。
```python
# sqlite3_custom_type.py
import pickle
import sqlite3

db_filename = 'todo.db'


def adapter_func(obj):
    """Convert from in-memory to storage representation.
    """
    print('adapter_func({})\n'.format(obj))
    return pickle.dumps(obj)


def converter_func(data):
    """Convert from storage to in-memory representation.
    """
    print('converter_func({!r})\n'.format(data))
    return pickle.loads(data)


class MyObj:

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return 'MyObj({!r})'.format(self.arg)


# Register the functions for manipulating the type.
sqlite3.register_adapter(MyObj, adapter_func)
sqlite3.register_converter("MyObj", converter_func)

# Create some objects to save.  Use a list of tuples so
# the sequence can be passed directly to executemany().
to_save = [
    (MyObj('this is a value to save'),),
    (MyObj(42),),
]

with sqlite3.connect(
        db_filename,
        detect_types=sqlite3.PARSE_DECLTYPES) as conn:
    # Create a table with column of type "MyObj"
    conn.execute("""
    create table if not exists obj (
        id    integer primary key autoincrement not null,
        data  MyObj
    )
    """)
    cursor = conn.cursor()

    # Insert the objects into the database
    cursor.executemany("insert into obj (data) values (?)",
                       to_save)

    # Query the database for the objects just saved
    cursor.execute("select id, data from obj")
    for obj_id, obj in cursor.fetchall():
        print('Retrieved', obj_id, obj)
        print('  with type', type(obj))
        print()
```
上面的示例程序使用pickle将一个对象转换为一个字符串后保存在数据库中，这对存储任意对象很有用，但是它不支持按对象属性查询。真正的对象关系映射器(ORM, object-relational mapper)，比如SQLAlchemy会将属性值存储在单独列中，这对大量数据更为有效。
```bash
$ python3 sqlite3_custom_type.py

adapter_func(MyObj('this is a value to save'))

adapter_func(MyObj(42))

converter_func(b'\x80\x03c__main__\nMyObj\nq\x00)\x81q\x01}q\x02X\x0
3\x00\x00\x00argq\x03X\x17\x00\x00\x00this is a value to saveq\x04sb
.')

converter_func(b'\x80\x03c__main__\nMyObj\nq\x00)\x81q\x01}q\x02X\x0
3\x00\x00\x00argq\x03K*sb.')

Retrieved 1 MyObj('this is a value to save')
  with type <class '__main__.MyObj'>

Retrieved 2 MyObj(42)
  with type <class '__main__.MyObj'>
```
##确定列类型
查询返回值的类型信息有两个来源。如前面我们所看到的，可以通过原表的声明来识别实际列的类型。另一种，我们还可以通过在查询的select子句中包含类型指示符，形式：as "name[type]"。
```python
# sqlite3_custom_type_column.py
import pickle
import sqlite3

db_filename = 'todo.db'


def adapter_func(obj):
    """Convert from in-memory to storage representation.
    """
    print('adapter_func({})\n'.format(obj))
    return pickle.dumps(obj)


def converter_func(data):
    """Convert from storage to in-memory representation.
    """
    print('converter_func({!r})\n'.format(data))
    return pickle.loads(data)


class MyObj:

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return 'MyObj({!r})'.format(self.arg)


# Register the functions for manipulating the type.
sqlite3.register_adapter(MyObj, adapter_func)
sqlite3.register_converter("MyObj", converter_func)

# Create some objects to save.  Use a list of tuples so we
# can pass this sequence directly to executemany().
to_save = [
    (MyObj('this is a value to save'),),
    (MyObj(42),),
]

with sqlite3.connect(
        db_filename,
        detect_types=sqlite3.PARSE_COLNAMES) as conn:
    # Create a table with column of type "text"
    conn.execute("""
    create table if not exists obj2 (
        id    integer primary key autoincrement not null,
        data  text
    )
    """)
    cursor = conn.cursor()

    # Insert the objects into the database
    cursor.executemany("insert into obj2 (data) values (?)",
                       to_save)

    # Query the database for the objects just saved,
    # using a type specifier to convert the text
    # to objects.
    cursor.execute(
        'select id, data as "pickle [MyObj]" from obj2',
    )
    for obj_id, obj in cursor.fetchall():
        print('Retrieved', obj_id, obj)
        print('  with type', type(obj))
        print()
```
当查询中有些类型与原表定义不同时，detect_types标志应使用PARSE_COLNAMES。
```bash
$ python3 sqlite3_custom_type_column.py

adapter_func(MyObj('this is a value to save'))

adapter_func(MyObj(42))

converter_func(b'\x80\x03c__main__\nMyObj\nq\x00)\x81q\x01}q\x02X\x0
3\x00\x00\x00argq\x03X\x17\x00\x00\x00this is a value to saveq\x04sb
.')

converter_func(b'\x80\x03c__main__\nMyObj\nq\x00)\x81q\x01}q\x02X\x0
3\x00\x00\x00argq\x03K*sb.')

Retrieved 1 MyObj('this is a value to save')
  with type <class '__main__.MyObj'>

Retrieved 2 MyObj(42)
  with type <class '__main__.MyObj'>
```
##事务
关系型数据库的关键特征之一就是使用事务维护一致的内部状态。启用事务时，我们通过连接对数据库所做的操作都不会影响到其他数据库的用户，知道我们将操作结果提交并刷新实际的数据库。
###保存更改
通过insert或update子句对数据库进行的更改，都需要我们显式地调用commit()才能被保存。这样的需求为应用提供了一个机会，可以将多个变更操作一起完成，这样他们就是以一种原子的方式保存而不是增量保存，这样做可以避免多个不同用户同时连接数据库只看到部分更新的情况。



































































