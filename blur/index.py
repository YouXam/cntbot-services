import json
import tempfile
from qcloud_cos_v5 import CosConfig, CosS3Client
from PIL import Image, ImageFilter
appid = 123456789
secret_id = 'secret_id'
secret_key = 'secret_key'
region = 'ap-region'
bucket = 'bucket'

client = CosS3Client(CosConfig(Secret_id=secret_id,
                     Secret_key=secret_key, Region=region))


def main_handler(event, context):
    try:
        print("start main handler")
        data = json.loads(event['body'])
        url = data["url"]
        blur = data["blur"]
        old_remote_path = url.split('myqcloud.com')[-1]
        ext = old_remote_path.split('.')[-1]
        tfile = tempfile.mkdtemp()
        old_local_path = tfile + '.' + ext
        new_local_path = tfile + '_blur.' + ext
        new_remote_path = '/'.join(old_remote_path.split('.')
                                   [:-1]) + '_blur.' + ext

        print("downloading: " + old_remote_path + ' -> ' + old_local_path)
        response = client.get_object(Bucket=bucket, Key=old_remote_path)
        response['Body'].get_stream_to_file(old_local_path)
        print("downloaded: " + old_remote_path + ' -> ' + old_local_path)

        print("bluring: " + old_local_path + ' -> ' + new_local_path)
        Image.open(old_local_path).filter(
            ImageFilter.GaussianBlur(float(blur))).save(new_local_path)
        print("blured" + old_local_path + ' -> ' + new_local_path)

        print("uploading: " + new_local_path + ' -> ' + new_remote_path)
        client.put_object_from_local_file(
            Bucket=bucket, LocalFilePath=new_local_path, Key=new_remote_path)
        print("uploaded: " + new_local_path + ' -> ' + new_remote_path)
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": 0,
                "url": f'https://{bucket}.cos.{region}.myqcloud.com{new_remote_path}',
                "key": new_remote_path
            }, ensure_ascii=False)
        }
    except Exception as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": 1,
                "msg": str(e)
            }, ensure_ascii=False)
        }
