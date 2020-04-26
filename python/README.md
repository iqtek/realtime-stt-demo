# VoiceKit Python examples

You will need Python >= 3.5 to run this examples.
To work correctly all scripts should be run from this directory.

## Usage

### Install the requirements


```
$ python3 -m pip install -r requirements.txt
```

You may install optional dependencies (`opuslib` and `PyAudio`) to gain additional functionality:

```
$ python3 -m pip install -r requirements/all.txt
```


## Generate Protobuf and gRPC definitions (optional)

In case of API changes (`*.proto` files in `apis` directory),
you may regenerate Protobuf and gRPC definitions by simply running the following script
(no need to re-clone the whole repo):

```
$ ./sh/generate_protobuf.sh
```
