# python连接FastDFS服务器的驱动
from fdfs_client.client import Fdfs_client
# 根据配置文件创建连接客户
client = Fdfs_client()
# 调用方法上传文件
result = client.upload_by_file('p2.jpg')
# 上传成功后返回结果
print(result)
'''
getting connection
<fdfs_client.connection.Connection object at 0x7f5eccd64cf8>
<fdfs_client.fdfs_protol.Tracker_header object at 0x7f5eccd64ba8>
{'Storage IP': '192.168.18.132', 'Remote file_id': 'group1/M00/00/00/wKgShFq9gIWAQr-7AAQWsfJVaO0846.jpg', 'Uploaded size': '261.00KB', 'Local file name': 'p2.jpg', 'Group name': 'group1', 'Status': 'Upload successed.'}

'''
