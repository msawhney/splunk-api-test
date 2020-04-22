from botocore.exceptions import ClientError
from datetime import date
import boto3
import splunk_client


class DataStore:
    def __init__(self):
        self.logger = splunk_client.get_logger()

    def upload_data(self, bucket_name, file_name, content, content_type):
        """
        This function uploads a file and its content to s3. Does some basic requirement check on filename format.
        """
        s3 = boto3.client('s3')
        try:
            if file_name.count('.') == 1:
                sep = file_name.split('.')
                sep[0] = sep[0] + date.today().isoformat()
                file_name = sep[0] + '.' + sep[1]
                self.logger.info('Uploading file: {} and content to s3 bucket: {}'.format(file_name, bucket_name))
                resp = s3.put_object(Bucket=bucket_name, Key=file_name, Body=content,
                                     ContentType=content_type)
                return resp
            else:
                raise ValueError('Invalid Filename extension')
        except ClientError as e:
            self.logger.debug(e)
