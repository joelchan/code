import boto3
import botocore
filename = 'src.zip'
bucket_name = 'matterhart-test'
s3_resource = boto3.resource('s3')
for bucket in s3_resource.buckets.all():
    print(bucket.name)
data = open(filename, 'rb')
s3_resource.Bucket(bucket_name).put_object(Key=filename, Body=data)

# try:
#     s3_resource.Bucket(bucket_name).download_file(filename, 'dbtable_posts2.p')
# except botocore.exceptions.ClientError as e:
#     if e.response['Error']['Code'] == "404":
#         print("The object does not exist.")
#     else:
#         raise

#%%