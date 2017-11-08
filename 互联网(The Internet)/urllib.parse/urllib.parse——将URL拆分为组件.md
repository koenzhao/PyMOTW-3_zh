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
当URL中有用户名和密码时，则它们是有效的，不设置它们则获取到None。主机名(hostname)即是网络位置(netloc)，全为小写并带有一个端口号。端口号会自动转换为一个整数值，如果没有则为None。
```bash
$ python3 urllib_parse_urlparseattrs.py

scheme  : http
netloc  : user:pwd@NetLoc:80
path    : /path
params  : param
query   : query=arg
fragment: frag
username: user
password: pwd
hostname: netloc
port    : 80
```
urlsplit()函数是urlparse()的变体。它的行为与urlparse()稍微有些不同，因为它不会从URL分解参数。这对于遵循RFC 2396的URL很有用，它支持对应路径的每一段参数。
```python
# urllib_parse_urlsplit.py
from urllib.parse import urlsplit

url = 'http://user:pwd@NetLoc:80/p1;para/p2;para?query=arg#frag'
parsed = urlsplit(url)
print(parsed)
print('scheme  :', parsed.scheme)
print('netloc  :', parsed.netloc)
print('path    :', parsed.path)
print('query   :', parsed.query)
print('fragment:', parsed.fragment)
print('username:', parsed.username)
print('password:', parsed.password)
print('hostname:', parsed.hostname)
print('port    :', parsed.port)
```
由于没有分解参数，元组API会显示5个参数而不是6个，这里没有params属性。
```bash
$ python3 urllib_parse_urlsplit.py

SplitResult(scheme='http', netloc='user:pwd@NetLoc:80',
path='/p1;para/p2;para', query='query=arg', fragment='frag')
scheme  : http
netloc  : user:pwd@NetLoc:80
path    : /p1;para/p2;para
query   : query=arg
fragment: frag
username: user
password: pwd
hostname: netloc
port    : 80
```
要从一个URL中剥离出片段标识符，如从一个URL中查找基页面名，可以使用urldefrag()。
```python
# urllib_parse_urldefrag.py
from urllib.parse import urldefrag

original = 'http://netloc/path;param?query=arg#frag'
print('original:', original)
d = urldefrag(original)
print('url     :', d.url)
print('fragment:', d.fragment)
```
返回值是一个基于命名元组的DefragResult类对象，包括URL基址和片段标识符。
```bash
$ python3 urllib_parse_urldefrag.py

original: http://netloc/path;param?query=arg#frag
url     : http://netloc/path;param?query=arg
fragment: frag
```
##反解析
有几种方法可以将各个分离的URL部分重新汇总到一个字符串中。用于解析的URL对象有一个geturl()方法。
```python
# urllib_parse_geturl.py
from urllib.parse import urlparse

original = 'http://netloc/path;param?query=arg#frag'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', parsed.geturl())
```
geturl()只能处理urlparse()和urlsplit()返回的对象。
```bash
$ python3 urllib_parse_geturl.py

ORIG  : http://netloc/path;param?query=arg#frag
PARSED: http://netloc/path;param?query=arg#frag
```
一个包含字符串的常规元组可以使用urlunparse()组合成一个URL。
```python
# urllib_parse_urlunparse.py
from urllib.parse import urlparse, urlunparse

original = 'http://netloc/path;param?query=arg#frag'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', type(parsed), parsed)
t = parsed[:]
print('TUPLE :', type(t), t)
print('NEW   :', urlunparse(t))
```
因为urlparse()返回的ParseResult类型对象可以当成一个元组使用，在上例中，我们显式地创建了一个新的元组来说明urlunparse()也能够处理正常的元组。
```bash
$ python3 urllib_parse_urlunparse.py

ORIG  : http://netloc/path;param?query=arg#frag
PARSED: <class 'urllib.parse.ParseResult'>
ParseResult(scheme='http', netloc='netloc', path='/path',
params='param', query='query=arg', fragment='frag')
TUPLE : <class 'tuple'> ('http', 'netloc', '/path', 'param',
'query=arg', 'frag')
NEW   : http://netloc/path;param?query=arg#frag
```
如果输入的URL包含多余的部分，在重建URL时会将这些部分舍弃。
```python
# urllib_parse_urlunparseextra.py
from urllib.parse import urlparse, urlunparse

original = 'http://netloc/path;?#'
print('ORIG  :', original)
parsed = urlparse(original)
print('PARSED:', type(parsed), parsed)
t = parsed[:]
print('TUPLE :', type(t), t)
print('NEW   :', urlunparse(t))
```
在上例中，原始URL中没有参数，查询和片段。新的url和原始url看起来不一起，但是它符合标准。
```bash
$ python3 urllib_parse_urlunparseextra.py

ORIG  : http://netloc/path;?#
PARSED: <class 'urllib.parse.ParseResult'>
ParseResult(scheme='http', netloc='netloc', path='/path',
params='', query='', fragment='')
TUPLE : <class 'tuple'> ('http', 'netloc', '/path', '', '', '')
NEW   : http://netloc/path
```
##连接













