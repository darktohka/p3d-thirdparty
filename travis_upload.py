import hashlib, traceback, os
import requests

class UploadAPI(object):

    def __init__(self, endpoint, auth_secret, chunk_size=8*1024*1024):
        self.endpoint = endpoint
        self.auth_secret = auth_secret
        self.chunk_size = chunk_size

    def post(self, *args, **kwargs):
        for i in range(10):
            try:
                req = requests.post(*args, **kwargs)
                
                if req.status_code != 200:
                    raise Exception('Error code {0}: {1}'.format(req.status_code, req.text))

                return req.json()
            except:
                print(traceback.format_exc())
                print('Trying again...')

        raise Exception('Failed to post data.')

    def upload_file(self, filename, target_filename=None):
        if target_filename is None:
            target_filename = os.path.basename(filename)

        md5 = hashlib.md5()
        start = 0
        end = -1
        length = os.path.getsize(filename)
        end_index = length - 1
        data = {'auth': self.auth_secret}

        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b''):
                md5.update(chunk)

                chunk_size = len(chunk)
                end += chunk_size

                headers = {'Content-Range': 'bytes {0}-{1}/{2}'.format(start, end, length)}
                start += chunk_size

                if end == end_index:
                    data['md5'] = md5.hexdigest()

                resp = self.post(self.endpoint, data=data, headers=headers, files={'file': (target_filename, chunk)})

                if 'url' in resp:
                    return resp['url']

                data['upload_id'] = resp['upload_id']

def main():
    api_endpoint = os.environ.get('DEPLOY_ENDPOINT')
    api_login = os.environ.get('DEPLOY_LOGIN')

    if not api_endpoint:
        raise Exception('Missing environment variable: DEPLOY_ENDPOINT')
    if not api_login:
        raise Exception('Missing environment variable: DEPLOY_LOGIN')

    import argparse
    parser = argparse.ArgumentParser('UploadAPI')
    parser.add_argument('filename', help='The file that will be uploaded.', type=str)
    parser.add_argument('target_filename', help='The file that will be uploaded.', type=str, nargs='?')
    args = parser.parse_args()

    api = UploadAPI(api_endpoint, api_login)
    url = api.upload_file(args.filename, args.target_filename)

    print(url)

if __name__ == '__main__':
    main()
