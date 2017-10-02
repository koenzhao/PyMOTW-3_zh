*目标：对逗号分隔值文件进行读写操作*
csv模块可用于从电子表格和数据库导出的数据，并写入采用字段和记录格式的文本文件。因为经常使用逗号分隔记录中的不同字段，所以这种格式通常称为逗号分隔值文件csv。
##读操作
使用reader()可以为一个csv文件的数据值创建一个对象。阅读器(reader)可以作为一个迭代器按顺序处理文件中的每一行数据。举个例子：
```python
# csv_reader.py
import csv
import sys

with open(sys.argv[1], 'rt') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```
reader()的第一个参数是文本行的源。在上面的例子中，源是一个文件，但实际上任何可迭代的对象均可作为第一个参数（比如一个StringIO实例，list等）。其他参数会影响输入数据的解析。
```bash
"Title 1","Title 2","Title 3","Title 4"
1,"a",08/18/07,"å"
2,"b",08/19/07,"∫"
3,"c",08/20/07,"ç"
```
当阅读器(reader)读完源数据后，输入的数据将被解析和转换成一个字符串列表。
```python
$ python3 csv_reader.py testdata.csv

['Title 1', 'Title 2', 'Title 3', 'Title 4']
['1', 'a', '08/18/07', 'å']
['2', 'b', '08/19/07', '∫']
['3', 'c', '08/20/07', 'ç']
```
解析器会处理嵌入在每一行(row)字符串中的换行符(line break)，这就是为什么处理后的行(row)不总是和输入源文件中的行(line)的内容相同。
```csv
"Title 1","Title 2","Title 3"
1,"first line
second line",08/18/07
```
输入中带有换行符的字段在解析器返回时会保留内部换行符。
```bash
$ python3 csv_reader.py testlinebreak.csv

['Title 1', 'Title 2', 'Title 3']
['1', 'first line\nsecond line', '08/18/07']
```
##写操作
对CSV文件进行写操作就像对它进行读操作一样简单。使用writer()为写操作创建一个对象，然后迭代每一行，使用writerow()将它们写入文件。
```python
# csv_writer.py
import csv
import sys

unicode_chars = 'å∫ç'

with open(sys.argv[1], 'wt') as f:
    writer = csv.writer(f)
    writer.writerow(('Title 1', 'Title 2', 'Title 3', 'Title 4'))
    for i in range(3):
        row = (
            i + 1,
            chr(ord('a') + i),
            '08/{:02d}/07'.format(i + 1),
            unicode_chars[i],
        )
        writer.writerow(row)

print(open(sys.argv[1], 'rt').read())
```
这个的输出和我们上面使用reader例子的输出不完全一样，因为它的某些值缺少引号。
```bash
$ python3 csv_writer.py testout.csv

Title 1,Title 2,Title 3,Title 4
1,a,08/01/07,å
2,b,08/02/07,∫
3,c,08/03/07,ç
```
##引号
对于writer来说，默认引号的行为是不同的，所以上一个例子中第2和第3列没有加引号。如果需要加引号，可以通过设置“引号参数(quoting argument)”设置其他引号模式之一。
```python
writer = csv.write(f, quoting = csv.QUOTE_NONNUMERIC)
```
在这种情况下，QUOTE_NONNUMERIC会为所有的非数字列加上引号。
```bash
$ python3 csv_writer_quoted.py testout_quoted.csv

"Title 1","Title 2","Title 3","Title 4"
1,"a","08/01/07","å"
2,"b","08/02/07","∫"
3,"c","08/03/07","ç"
```
我们有4种不同的引号选项，定义为csv模块中的常量。
* QUOTE_ALL:不考虑类型，给所有的列加引号。
* QUOTE_MINIMAL:这个是默认选项，给所有包含特殊字符的段加引号（特殊字符指，对于相同的方言和配置的解析器，会引起混淆的字符）。
* QUOTE_NONNUMERIC:对所有的非数字字段加引号。当使用reader时，没有加引号的字段会被转换成浮点数。
* QUOTE_NONE:对输出的所有内容都不加引号。当使用reader时，引号字符包含在字段值中（正常情况下，他们会处理为定界符并去除）。

##方言
对于逗号分隔值文件没有明确的定义，所以我们的解析器必须很灵活。这里的灵活是指，我们可以通过很多参数设置去控制如何解析csv文件或写数据。这些参数不会一个一个这样地传给reader或writer，而是会组合成一个方言(dialect)对象传入。
方言(dialect)对象可以通过名字注册，所以csv模块的调用者(caller)不需要提前知道设置的参数。可以使用list_dialects()获取完整的已注册方言(dialect)列表。
```python
# csv_list_dialects.py

import csv

print(csv.list_dialects())
```
标准库包括三个方言(dialect):excel,excel-tabs,和unix。excel方言(dialect)可以处理Microsoft Excel和LibreOffice默认输出格式的数据。unix方言(dialect)会用双引号将所有字段括起来，使用“\n”做为记录分隔符。
```bash
$ python3 csv_list_dialects.py

['excel', 'excel-tab', 'unix']
```
####创建一个方言(dialect)
如果输入文件使用管道(|)分隔字段，而不是使用逗号，如下：
```csv
"Title 1"|"Title 2"|"Title 3"
1|"first line
second line"|08/18/07
```
通过使用适当的分隔符，我们能够注册一个新的方言(dialect)。
```python
# csv_dialect.py
import csv

csv.register_dialect('pipes', delimiter='|')

with open('testdata.pipes', 'r') as f:
    reader = csv.reader(f, dialect='pipes')
    for row in reader:
        print(row)
```
通过"pipes"方言(dialect)，文件就可以像CSV文件一样读取。
```bash
$ python3 csv_dialect.py

['Title 1', 'Title 2', 'Title 3']
['1', 'first line\nsecond line', '08/18/07']
```
####方言参数
一个方言指定了解析或写入一个数据文件的记号(token)。下表列出了可以指定文件格式的各个方面，从列分隔符到转义字符。
CSV方言参数
|属性|缺省值|含义|
|:-|:-|:-|
|delimiter|,|字段分隔符(一个字符)|
|doublequote|True|这个标志控制quotechar是否成对|
|escapechar|None|这个字符用来指示一个转义字符|
|lineterminator|\r\n|writer使用这个字符串来标志一行的终止|
|quotechar|"|这个字符用来包围特殊值的字段(一个字符)|
|quoting|QUOTE_MINIMAL|控制前面说到的引号行为|
|skipinitialspace|Fasle|忽略字段分隔符后面的空白符|
```python
csv_dialect_variations.py
import csv
import sys

csv.register_dialect('escaped',
                     escapechar='\\',
                     doublequote=False,
                     quoting=csv.QUOTE_NONE,
                     )
csv.register_dialect('singlequote',
                     quotechar="'",
                     quoting=csv.QUOTE_ALL,
                     )

quoting_modes = {
    getattr(csv, n): n
    for n in dir(csv)
    if n.startswith('QUOTE_')
}

TEMPLATE = '''\
Dialect: "{name}"

  delimiter   = {dl!r:<6}    skipinitialspace = {si!r}
  doublequote = {dq!r:<6}    quoting          = {qu}
  quotechar   = {qc!r:<6}    lineterminator   = {lt!r}
  escapechar  = {ec!r:<6}
'''

for name in sorted(csv.list_dialects()):
    dialect = csv.get_dialect(name)

    print(TEMPLATE.format(
        name=name,
        dl=dialect.delimiter,
        si=dialect.skipinitialspace,
        dq=dialect.doublequote,
        qu=quoting_modes[dialect.quoting],
        qc=dialect.quotechar,
        lt=dialect.lineterminator,
        ec=dialect.escapechar,
    ))

    writer = csv.writer(sys.stdout, dialect=dialect)
    writer.writerow(
        ('col1', 1, '10/01/2010',
         'Special chars: " \' {} to parse'.format(
             dialect.delimiter))
    )
    print()
```
上面的程序使用多种不同的方言格式化输出相同的数据。
```bash
$ python3 csv_dialect_variations.py

Dialect: "escaped"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 0         quoting          = QUOTE_NONE
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = '\\'

col1,1,10/01/2010,Special chars: \" ' \, to parse

Dialect: "excel"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_MINIMAL
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = None

col1,1,10/01/2010,"Special chars: "" ' , to parse"

Dialect: "excel-tab"

  delimiter   = '\t'      skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_MINIMAL
  quotechar   = '"'       lineterminator   = '\r\n'
  escapechar  = None

col1    1       10/01/2010      "Special chars: "" '     to parse"

Dialect: "singlequote"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_ALL
  quotechar   = "'"       lineterminator   = '\r\n'
  escapechar  = None

'col1','1','10/01/2010','Special chars: " '' , to parse'

Dialect: "unix"

  delimiter   = ','       skipinitialspace = 0
  doublequote = 1         quoting          = QUOTE_ALL
  quotechar   = '"'       lineterminator   = '\n'
  escapechar  = None

"col1","1","10/01/2010","Special chars: "" ' , to parse"
```
####方言自动检测
为输入文件配置好方言(dialect)设置最好的方法就是提前知道需要设置的内容。对于设置方言参数的一些未知数据，Sniffer类(嗅探器类)可以做出有根据的推测。sniff()方法取一段输入数据作为样本，可选参数给出可能的分隔字符。
```python
# csv_dialect_sniffer.py
import csv
from io import StringIO
import textwrap

csv.register_dialect('escaped',
                     escapechar='\\',
                     doublequote=False,
                     quoting=csv.QUOTE_NONE)
csv.register_dialect('singlequote',
                     quotechar="'",
                     quoting=csv.QUOTE_ALL)

# Generate sample data for all known dialects
samples = []
for name in sorted(csv.list_dialects()):
    buffer = StringIO()
    dialect = csv.get_dialect(name)
    writer = csv.writer(buffer, dialect=dialect)
    writer.writerow(
        ('col1', 1, '10/01/2010',
         'Special chars " \' {} to parse'.format(
             dialect.delimiter))
    )
    samples.append((name, dialect, buffer.getvalue()))

# Guess the dialect for a given sample, and then use the results
# to parse the data.
sniffer = csv.Sniffer()
for name, expected, sample in samples:
    print('Dialect: "{}"'.format(name))
    print('In: {}'.format(sample.rstrip()))
    dialect = sniffer.sniff(sample, delimiters=',\t')
    reader = csv.reader(StringIO(sample), dialect=dialect)
    print('Parsed:\n  {}\n'.format(
          '\n  '.join(repr(r) for r in next(reader))))
```
sniff()方法返回一个带有用于解析数据的配置的方言实例。每次结果不总是完美的，如上面例子中的“转义”方言所示。
```bash
$ python3 csv_dialect_sniffer.py

Dialect: "escaped"
In: col1,1,10/01/2010,Special chars \" ' \, to parse
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars \\" \' \\'
  ' to parse'

Dialect: "excel"
In: col1,1,10/01/2010,"Special chars "" ' , to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'

Dialect: "excel-tab"
In: col1        1       10/01/2010      "Special chars "" '      to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' \t to parse'

Dialect: "singlequote"
In: 'col1','1','10/01/2010','Special chars " '' , to parse'
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'

Dialect: "unix"
In: "col1","1","10/01/2010","Special chars "" ' , to parse"
Parsed:
  'col1'
  '1'
  '10/01/2010'
  'Special chars " \' , to parse'
```
##使用字段名
除了处理数据序列，CSV模块包含的类会将数据行处理为字典，以便字段可以命名。DictReader和DictWriter类将数据行翻译成字典而不是列表。可以将字典的键值(key)可以由我们传入，也可以通过输入数据的第一行推断出（当首行是标题行）。
```python
# csv_dictreader.py
import csv
import sys

with open(sys.argv[1], 'rt') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
```
基于字典的reader和writer是使用基于序列的类，相同的方法和参数实现的包装类。唯一不同的地方在，reader的API返回的数据行(rows)是字典，而不是列表或元组。
```bash
$ python3 csv_dictreader.py testdata.csv

{'Title 2': 'a', 'Title 3': '08/18/07', 'Title 4': 'å', 'Title 1
': '1'}
{'Title 2': 'b', 'Title 3': '08/19/07', 'Title 4': '∫', 'Title 1
': '2'}
{'Title 2': 'c', 'Title 3': '08/20/07', 'Title 4': 'ç', 'Title 1
': '3'}
```
DictWriter则必须给出字段名称列表，以便它能够知道在输出时候的列顺序。
```python
# csv_dictwriter.py
import csv
import sys

fieldnames = ('Title 1', 'Title 2', 'Title 3', 'Title 4')
headers = {
    n: n
    for n in fieldnames
}
unicode_chars = 'å∫ç'

with open(sys.argv[1], 'wt') as f:

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(3):
        writer.writerow({
            'Title 1': i + 1,
            'Title 2': chr(ord('a') + i),
            'Title 3': '08/{:02d}/07'.format(i + 1),
            'Title 4': unicode_chars[i],
        })

print(open(sys.argv[1], 'rt').read())
```
字段名不会自动写入文件，但可以通过writeheader()方法显示写入。
```bash
$ python3 csv_dictwriter.py testout.csv

Title 1,Title 2,Title 3,Title 4
1,a,08/01/07,å
2,b,08/02/07,∫
3,c,08/03/07,ç
```

























