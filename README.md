# py-w3

This is a reimplementation of the web3.storage HTTP api.

There is an existing implementation at https://pypi.org/project/web3storage, but at the time of writing it did not have an
associated public source repository.

This project's source repository is at https://github.com/xloem/py-w3storage, and auto-merging of pull requests is enabled.

The API is open to any changes or improvements.

The official library at https://www.npmjs.com/package/web3.storage could be used as a baseline for such improvements.

## examples

```python
import w3storage

w3 = w3storage.API(token='w3-api-token')

some_uploads = w3.user_uploads(size=25)

# limited to 100 MB
helloworld_cid = w3.post_upload(('hello_World.txt', 'Hello, world.'))
readme_cid = w3.post_upload(('README.md', open('README.md', 'rb')))

# larger files can be uploaded by splitting them into .cars.
```
