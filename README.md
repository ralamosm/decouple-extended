# decouple-extended: Simple extensions for python-decouple

This package provides some extensions for `python-decouple`.

In this package you will find two new `python-decouple` repositories:

* `RepositoryAWSParameterStore`
* `RepositoryAWSSecrets`

which as their names show, made use of AWS' Systems Manager (Parameter Store) and Secrets respectively.

Please note that these classes are initialized by passing one parameter name or secret name, which value is assumed to be an object (a python dict), and so when you retrieve config keys with `config('KEY)`, what you are really doing is getting keys from that object, not different AWS parameters or secrets.

Besides these repositories, `decouple-extended` also provides CRUD equivalents to the well-known `python-decouple` classes, as well as the new repositories provided by this package:

* `CRUDConfig`
* `CRUDRepositoryEnv`
* `CRUDRepositoryIni`
* `CRUDAWSSecrets`
* `CRUDAWSParameterStore`

## Usage

You can use the CRUD extensions as you would usually use `python-decouple`'s

```python
import json
from decouple_extended import CRUDConfig, CRUDRepositoryAWSSecrets

repo = CRUDRepositoryAWSSecrets('secret_name')
config = CRUDConfig(repo)

# reading database config as a dict
DATABASE = config('DATABASE', cast=json.loads)

# setting (or updating) a key
config.set('CACHE', {'host': 'localhost', 'backend': 'memcache'})

# deleting a key
config.delete('EXPERIMENTS')
```

and you can also use the normal `Repository*` classes, without 'CRUD', with usual `python-decouple`

```python
import json
from decouple import Config
from decouple_extended import RepositoryAWSParameterStore

repo = RepositoryAWSParameterStore('parameter_name')
config = Config(repo)

# You can just read in this case
DATABASE = config('DATABASE', cast=json.loads)
```
