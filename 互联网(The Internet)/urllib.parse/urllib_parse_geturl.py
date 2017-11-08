# urllib_parse_geturl.py

from urllib.parse import urlparse

original = 'http://netloc/path;param?query=arg#frag'
print('ORIG:',original)
parsed = urlparse(original)
print('PARSED:', parsed.geturl())
