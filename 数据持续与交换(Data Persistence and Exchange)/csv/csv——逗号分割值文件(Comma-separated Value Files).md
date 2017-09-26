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


































