# urllib.parse_urldefrag.py

from urllib.parse import urldefrag

original = 'http://netloc/path;para?query=arg#frag'
print('original:', original)
d = urldefrag(original)
print('url:',d.url)
print('fragment:',d.fragment)
