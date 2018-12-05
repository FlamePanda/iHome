from fdfs_client.client import get_tracker_conf
from fdfs_client.client import Fdfs_client
from ihome.constants import FASTFDFS_CONFIG_PATH

# 分布式文件存储类
class Storage(object):
	'''用于存储用户的图片数据'''
	instance = None	

	def __new__(cls):
		'''单例模式'''
		if cls.instance is None:
			obj = super().__new__(cls)
			obj._client = Fdfs_client(get_tracker_conf(FASTFDFS_CONFIG_PATH))
			cls.instance = obj
		return cls.instance

	def upload_file(self,filedata):
		'''上传图片
		params:二进制的图片数据
		return:上传成功，返回文件存贮id，失败，返回None
		'''
		if not filedata:
			raise Exception('file data not None!')
	
		res = self._client.upload_by_buffer(filedata)
		if not res or res.get('Status') != 'Upload successed.':
			raise Exception('文件上传失败！')
		else:
			filename = res.get('Remote file_id').decode('utf-8')
		return filename
	
	def delete_file(self,filename):
		'''删除图片
		params:文件ID
		return:None
			'''
		if not filename:
			raise Exception('file name not None!')
		res = self._client.delete_file(filename)
		if 'Delete file successed.' in res:
			return True
		else:
			return False
