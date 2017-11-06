目标：将URL拆分为组件

urllib.parse模块提供了操作URL及其组成部分的功能，可以将它们分解或组装起来。

##解析
urlparse()函数返回一个ParseResult对象，它类似一个包含6个元素的元组。
```python
# urllib_parse_urlparse.py
from urllib.parse import urlparse

url = 'http://netloc/path;param?query=arg#frag'
parsed = urlparse(url)
print(parsed)
```
通过元组接口得到的URL部分分别是机制、网络位置、路径、路径段参数（有一个分号与路径分开）、查询和片段。
```bash
$ python3 urllib_parse_urlparse.py

ParseResult(scheme='http', netloc='netloc', path='/path',
params='param', query='query=arg', fragment='frag')
```
尽管返回值像是一个元组，实际上它基于命名元组，这是一种支持通过下标索引和名字属性去访问URL各个部分的元组派生类。属性API不仅对开发人员来说易于使用，还允许访问tuple API未提供的很多值。
```python
# urllib_parse_urlparseattrs.py
from urllib.parse import urlparse

url = 'http://user:pwd@NetLoc:80/path;param?query=arg#frag'
parsed = urlparse(url)
print('scheme  :', parsed.scheme)
print('netloc  :', parsed.netloc)
print('path    :', parsed.path)
print('params  :', parsed.params)
print('query   :', parsed.query)
print('fragment:', parsed.fragment)
print('username:', parsed.username)
print('password:', parsed.password)
print('hostname:', parsed.hostname)
print('port    :', parsed.port)
```
























