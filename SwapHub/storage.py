from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True
    querystring_auth = False

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True
    querystring_auth = False
    default_acl = 'public-read'
    
    def url(self, name, parameters=None, expire=None):
        url = super().url(name, parameters, expire)
        if url.startswith('https://swaphub-media.s3.us-east-1.amazonaws.com/media/'):
            return url
        return url.replace('https://swaphub-media.s3.amazonaws.com/', 'https://swaphub-media.s3.us-east-1.amazonaws.com/')
