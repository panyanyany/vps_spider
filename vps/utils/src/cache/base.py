import os
import random
import json
import urllib
import hashlib
import pickle

from utils.src import url_util


CACHE_DIR = '.cache'

def setup(cache_dir='.cache'):
    global CACHE_DIR
    CACHE_DIR = cache_dir or CACHE_DIR

class Base:
    cache_dir = CACHE_DIR

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir or self.cache_dir

    def get(self, key): pass
    def getAll(self): pass
    def calcKey(self, key): pass


# cache using files
class FileCache(Base):

    def __init__(self, cache_dir, file_mode='t'):
        super().__init__(cache_dir)
        self.file_mode = file_mode

    def calcKey(self, key):
        raise NotImplementedError()

    def get(self, key):
        path = self.calcKey(key)
        if not os.path.exists(path):
            return None

        body = ''
        file_mode = 'r' + self.file_mode
        with open(path, file_mode) as fp:
            body = fp.read()
        return body
    
    def set(self, key, body):
        path = self.calcKey(key)
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_mode = 'w' + self.file_mode + '+'
        with open(path, file_mode) as fp:
            fp.write(body)

    # get all file pathes
    def _getKeys(self):
        keys = []
        for dir, dirnames, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                if filename.endswith(self.fileType):
                    keys.append(os.path.join(dir, filenaame))
        return keys

    # get all uids, which could be passed to self.get(uid)
    def getKeys(self):
        pathes = self._getKeys()
        keys = []
        for path in pathes:
            key = os.path.split(path)[-1].split('.')[0]
            keys.append(key)
        return keys

    def getValues(self):
        users = []
        for entry_path in self._getKeys():
            d = {}
            with open(entry_path) as fp:
                d = json.load(fp)

            users.append(d)
        return users


# store obj as file, group by its integer ID
class IdFileCache(FileCache):
    groupBy = 50
    fileType = '.json'

    def calcKey(self, uid):
        uid = int(uid)
        levels = self.calcDirs(uid, self.groupBy)[:-1]
        groupKey = '/'.join(map(lambda e: '%02d' % e, levels))
        path = '{root}/{groupKey}/{uid:011}{fileType}'.format(root=self.cache_dir, uid=uid, groupKey=groupKey, fileType=fileType)
        return path

    def calcLevel(self, tot, groupBy):
        level = 1
        while True:
            if tot < groupBy: break
            tot /= groupBy 
            level += 1
        return level

    def calcDirs(self, uid, groupBy):
        keys = []
        level = self.calcLevel(uid, groupBy)
        for i in range(level):
            keys.append(uid % groupBy)
            uid /= groupBy

        return keys


# store obj as file, group by its integer ID
class WebsiteFileCache(FileCache):
    fileType = '.html'

    def calcKey(self, url):
        """
        Split url by path segments and with sanitizing
        Join path segments as file path
        Join md5 of url as file name
        """
        parsedUrl = urllib.parse.urlparse(url)

        segs = [parsedUrl.netloc] + parsedUrl.path.split('/')
        path = os.path.join(*[url_util.toFileName(e) for e in segs])
        m = hashlib.sha256()
        m.update(url.encode('utf8'))
        hashcode = m.hexdigest()[:8]
        
        filePath = os.path.join(self.cache_dir, path, hashcode + self.fileType)
        return filePath

