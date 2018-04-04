from haystack import indexes
from .models import GoodsSKU

class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    """建立索引时被使用的类"""
    # document=True表示建立的索引数据存储到文件中
    # use_template=True表示通过模板制定表中的字段，用于查询
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """从哪个表中查询"""
        return GoodsSKU

    # 针对那些行进行查询
    def index_queryset(self, using=None):
        """返回要建立索引的数据"""
        return self.get_model().objects.all()