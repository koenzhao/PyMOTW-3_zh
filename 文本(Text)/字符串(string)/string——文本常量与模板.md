目的：包含用于处理文本的常量和类
string模块是从最早期版本的Python开始存在的。很多早期在string模块中实现的功能现在已经移植到了str对象方法中。目前string模块保留了几个在处理str对象时很有用的常量和类。下面我们将集中讨论这几个常量和类。
##函数
capwords()函数能将一个字符串中每一个单词的首字母大写。
```python
# string_capwords.py

import string

s = 'The quick brown fox jumped over the lazy dog.'

print(s)
print(string.capwords(s))
```
输出的结果就像是先调用split()获得分词结果，然后再将返回列表中的每一个单词大写，最后再使用join()方法将结果组合起来。
```bash
$ python3 string_capwords.py

The quick brown fox jumped over the lazy dog.
The Quick Brown Fox Jumped Over The Lazy Dog.
```
##模板
字符串模板是PEP 292规范的一部分，并替代原来的内置插值语法。





































































































































