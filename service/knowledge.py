from whoosh  import highlight
from whoosh.filedb.filestore import FileStorage
storage = FileStorage('knowdata')
ix = storage.open_index()
my_cf = highlight.ContextFragmenter(maxchars=100, surround=50)
def find_whoosh(s):
    with ix.searcher() as searcher:
        results=searcher.find("content", s)
        results.fragmenter.charlimit = None
        results.fragmenter = my_cf
        results.formatter =highlight.UppercaseFormatter()
        return [{'title':results[i]["title"],'content':results[i].highlights("content")} for i in range(min(3, len(results)))]
