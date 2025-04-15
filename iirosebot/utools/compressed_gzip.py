import gzip
import io


def compress_data(data):
    # 创建一个内存流对象
    compressed_data = io.BytesIO()

    # 使用gzip压缩数据
    with gzip.GzipFile(fileobj=compressed_data, mode='wb') as f:
        f.write(data.encode('utf-8'))

    # 获取压缩后的数据并转换为字节型
    compressed_bytes = compressed_data.getvalue()

    return compressed_bytes
