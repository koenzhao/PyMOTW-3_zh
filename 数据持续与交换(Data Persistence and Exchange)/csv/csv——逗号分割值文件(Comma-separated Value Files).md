目标：对逗号分隔值文件进行读写操作
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






























