# Django中提供的文件存储类的基类
from django.core.files.storage import Storage
from django.conf import settings
# 自定义存储类，将内容存储到fastdfs
# python连接FastDFS服务器的驱动
from fdfs_client.client import Fdfs_client


class FdfsStorage(Storage):
    def save(self, name, content, max_length=None):
        # 从网络流中读取文件数据
        buffer = content.read()
        # 根据配置文件创建链接的客户端
        client = Fdfs_client(settings.FDFS_CLIENT)
        # 调用方法上传文件
        # result = client.upload_by_file('p2.jpg')
        try:
            result = client.upload_by_buffer(buffer)
        except:
            raise
        '''
        {'Storage IP': '192.168.18.132', 'Remote file_id': 'group1/M00/00/00/wKgShFq9gIWAQr-7AAQWsfJVaO0846.jpg',
         'Uploaded size': '261.00KB', 'Local file name': 'p2.jpg', 'Group name': 'group1', 'Status': 'Upload successed.'}

        '''

        if result.get('Status') == 'Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('上传文件失败')


    def url(self, name):
        return settings.FDFS_SERVER+name
