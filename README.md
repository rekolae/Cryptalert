# Cryptalert V1.0.0

Python application that fetches cryptocurrency data and notifies the user through discord. The application operation is
configurable: TUI (Text UI) and Discord bot can both be enabled at the same time, or one of the two can be turned off.

Everyone is welcome to take part in the project, but please read through the CONTRIBUTING file for extra information and guidelines.

## Installation and usage

This package can be installed or run standalone, only difference how the bot can be started.
If the package is installed -> it can be run anywhere, if not -> startup script must be run.

Use of a [venv](https://docs.python.org/3/tutorial/venv.html "Virtual Environments in Python")
is strongly recommended to keep the base python clean.


### Installing the package

This package can be installed to be run anywhere, installation works as follows

```
cd Cryptalert                                   # cd into the source root
python -m pip install .                         # Install using pip
```

After installation the package can be run from anywhere as simply as:

```
python -m cryptalert <flags>                    # Start application
```


### Running the package without installing

If module installation is not preferred, you must first install required packages:

```
cd Cryptalert                                   # cd into the source root
python -m pip install -r requirements.txt       # Install using pip
```

After which you can start the bot by running the startup script:

```
python cryptalert/app.py <flags>                # Start application
```