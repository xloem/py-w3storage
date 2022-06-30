# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import requests

class _BearerAuth(requests.auth.AuthBase):
    def __init__(self, key):
        self.key = key
    def __call__(self, r):
        r.headers['authorization'] = 'Bearer ' + self.key
        return r

class W3Exception(Exception):
    def __init__(self, response, *params):
        try:
            json = response.json()
            params = (json['name'], json['message'], *params)
        except:
            params = (response.text, *params)
        super().__init__(*params)

class W3BadRequest(W3Exception):
    pass

class W3Unauthorized(W3Exception):
    pass

class W3Forbidden(W3Exception):
    pass

class W3InternalServerError(W3Exception):
    pass

class W3HTTPError(W3Exception):
    pass

'''
This documentation was copied by hand based on
https://web3.storage/docs/reference/http-api/, and could likely be improved.

Notably there is an unincluded section at the bottom of that page specifying
all the return objects.
'''

class API:
    def __init__(self, token = None, url = 'https://api.web3.storage'):
        self._url = url
        self._auth = _BearerAuth(token) if token is not None else None
    def post_car(self, car, name=None):
        '''
        Upload a CAR[1] (Content Addressable aRchive) file and store the IPFS
        DAG[2] (Directed Acyclic Graph) it contains.

        See the Working with Content Archives guide[3] for details on creating
        CARs and splitting them into chunks for upload using the carbites
        JavaScript API[4], command line tool[5], or Go library[6].

        Requests to this endpoint have a maximum payload size of 100MB but
        partial DAGs are supported, so multiple CAR files with the same root
        but with different sub-trees can be sent. This enables uploading of
        files that are bigger than the maximum payload size.

        Note that only one CAR can be uploaded at a time, and only CAR files
        are accepted. This is in contrast to .post_upload(), which can upload
        multiple files at once and accepts both CAR files and files from the
        client.

        You can also provide a name for the file.

        Returns: CID of upload as str.

        1: https://ipld.io/specs/transport/car/
        2: https://docs.ipfs.io/concepts/merkle-dag/
        3: https://web3.storage/docs/how-tos/work-with-car-files
        4: https://github.com/nftstorage/carbites
        5: https://github.com/nftstorage/carbites-cli/
        6: https://github.com/alanshaw/go-carbites
        '''
        headers = {}
        if name is not None:
            headers['X-NAME'] = requests.utils.quote(name)
        r = self._post(
            'upload',
            data = car,
            headers = headers
        )
        return r.json()['cid']

    def car(self, cid):
        '''
        Retrieve an IPFS DAG[1] (Directed Acyclic Graph) packaged in a CAR
        file, supplying the CID of the data you are interested in.

        1: https://docs.ipfs.io/concepts/merkle-dag/

        Returns: bytes
        '''
        r = self._get('car', str(cid))
        return r.content

    def head_car(self, cid):
        '''
        This method is useful for doing a dry run of a call to .car().
        Because it only returns HTTP header information, it is far more
        lightweight and can be used to get only the metadata about the given
        CAR file without retrieving a whole payload.

        Returns: int size of bytes
        '''
        r = self._head('car', str(cid))
        return int(r['Content-Length'])

    def status(self, cid):
        '''
        Retrieve metadata about a specific file by using .status(cid),
        supplying the CID of the file you are interested in. This metadata
        includes the creation date and file size, as well as details about how
        the network is storing your data. Using this information, you can
        identify peers on the IPFS (InterPlanetary File System)[1] network that
        are pinning the data, and Filecoin[2] storage providers that have accepted
        deals to store the data.

        Returns: {
            'cid': str,
            'dagSize': int,
            'created': iso date str,
            'pins': [
                {
                    'peerId': str,
                    'peerName': str,
                    'region': str,
                    'status': str,
                    'updated': iso date str
                }
            ],
            'deals': [
                {
                    'dealId': int,
                    'storageProvider': str,
                    'status': str,
                    'pieceCid': str,
                    'dataCid': str,
                    'dataModelSelector': str,
                    'activation': iso date str,
                    'created': iso date str,
                    'updated': iso date str
                }
            ]
        }

        1: https://ipfs.io/
        2: https://filecoin.io/
        '''
        r = self._get('status', str(cid))
        return r.json()

    def post_upload(self, *files):
        '''
        Store files using Web3.Storage. You can upload either a single file or
        multiple files.

        Files may be provided as raw data or a tuple of (filename, filedata,
        optional_content_type, optional_headers). A file object opened in
        binary mode may be passed to read from the object.

        Requests to this endpoint have a maximum payload size of 100MB. To
        upload larger files, see the documentation for the .post_car().

        Returns: CID of upload as str
        '''
        r = self._post(
            'upload',
            files=[
                ('file', file)
                for file in files
            ]
        )
        return r.json()['cid']

    def user_uploads(self, before: str = None, size: int = None):
        '''
        Lists all previous uploads for the account ordered by creation date,
        newest first. These results can be paginated by specifying before and
        size parameters, using the creation date associated with the oldest
        upload returned in each batch as the value of before in subsequent
        calls.

        Note this endpoint returns all uploads for the account not just the API
        key in use.

        The information returned includes the creation date and file size, as
        well as details about how the network is storing your data. Using this
        information, you can identify peers on the IPFS (InterPlanetary File
        System)[1] network that are pinning the data, and Filecoin[2] storage
        providers that have accepted deals to store the data.


        before: str
    
            Specifies a date, in ISO 8601 format. Ensures that the call to
            .user_uploads() will not return any results newer than the
            given date.
    
            Example: "2020-07-27T17:32:28Z"
    
        size: int

            Specifies the maximum number of uploads to return.

            Default value: 25

        Return: list

            [
              {
                "cid": "bafkreidivzimqfqtoqxkrpge6bjyhlvxqs3rhe73owtmdulaxr5do5in7u",
                "dagSize": 132614,
                "created": "2021-03-12T17:03:07.787Z",
                "pins": [
                  {
                    "peerId": "12D3KooWMbibcXHwkSjgV7VZ8TMfDKi6pZvmi97P83ZwHm9LEsvV",
                    "peerName": "web3-storage-dc13",
                    "region": "US-DC",
                    "status": "PinQueued",
                    "updated": "2021-03-12T17:03:07.787Z"
                  }
                ],
                "deals": [
                  {
                    "dealId": 138,
                    "storageProvider": "f05678",
                    "status": "Queued",
                    "pieceCid": "bafkreidivzimqfqtoqxkrpge6bjyhlvxqs3rhe73owtmdulaxr5do5in7u",
                    "dataCid": "bafkreidivzimqfqtoqxkrpge6bjyhlvxqs3rhe73owtmdulaxr5do5in7u",
                    "dataModelSelector": "Links/100/Hash/Links/0/Hash/Links/0/Hash",
                    "activation": "2021-03-18T11:46:50.000Z",
                    "created": "2021-03-18T11:46:50.000Z",
                    "updated": "2021-03-18T11:46:50.000Z"
                  }
                ]
              }
            ]

        1: https://ipfs.io/
        2: https://filecoin.io/
        '''
        params = {}
        if before is not None:
            if type(before) is int:
                before = datetime.datetime.fromtimestamp()
            elif type(before) is str:
                before = datetime.datetime.fromisoformat(before)
            before = before.isoformat()
            params['before'] = before
        if size is not None:
            params['size'] = int(size)
        r = self._get('user', 'uploads', params=params)
        return r.json()

    def _head(self, *params, **kwparams):
        return self._request(*params, method='HEAD', **kwparams)
    def _get(self, *params, **kwparams):
        return self._request(*params, method='GET', **kwparams)
    def _post(self, *params, **kwparams):
        return self._request(*params, method='POST', **kwparams)
    def _request(self, *params, **kwparams):
        params = (self._url, *params)
        if self._auth is not None and 'auth' not in kwparams:
            kwparams['auth'] = self._auth
        r = requests.request(url='/'.join(params), **kwparams)
        try:
            r.raise_for_status()
            return r
        except Exception as exception:
            http_exception = exception
        if r.status_code == 400:
            raise W3BadRequest(r)
        elif r.status_code == 401:
            raise W3Unauthorized(r)
        elif r.status_code == 403:
            raise W3Forbidden(r)
        elif r.status_code >= 500 and r.status_code < 600:
            raise W3InternalServerError(r)
        else:
            raise W3HTTPError(r, r.status_code, http_exception)
