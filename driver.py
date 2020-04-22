import splunk_src
import splunk_src.splunk_client as splunk_client
# import splunk_src.data_store as store
import uuid


def export_splunk_data_to_s3():
    saved_query = splunk_src.get_setting('SPLUNK_SAVED_SEARCH')
    splunk = splunk_client.SplunkIngestion()
    response = splunk.execute_saved_query(saved_query)

    # data_store = store.DataStore()
    # bucket = splunk_src.get_setting('SPLUNK_S3_BUCKET')
    file_name = '-'.join([str(uuid.uuid4().hex[:6]), 'splunk'+'.json'])
    # data_store.upload_data
    #       (bucket_name=bucket, file_name=file_name, content=response, content_type='application/json')
    with open(file=file_name, mode='w') as json_file:
        json_file.write(response)
    splunk_src.get_logger().info('SUCCESS')


if __name__ == '__main__':
    export_splunk_data_to_s3()
