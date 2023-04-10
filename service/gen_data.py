import os
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
from whoosh.filedb.filestore import FileStorage

def gen_whoosh_data():
    floder='knowledge'
    files=os.listdir(floder)
    analyzer = ChineseAnalyzer()
    schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True, analyzer=analyzer))
    storage = FileStorage('knowdata')
    if not os.path.exists('knowdata'):
        os.mkdir('knowdata')
        ix = storage.create_index(schema)
    else:
        ix = storage.open_index()

    writer = ix.writer()
    for file in files:
        try:
            with open(floder+'/'+file,"r",encoding='utf-16') as f:  
                data = f.read()
        except:
                with open(floder+'/'+file,"r",encoding='utf-8') as f:  
                    data = f.read()
        writer.add_document(title=file, content=data)

    writer.commit()  # 提交
    print("读取知识库文件完成")


if __name__ == "__main__":
    gen_whoosh_data()
