# Developing Your First Tutoron

## Launch the server

For all Django commands, once you've created the virtual
environment, make sure that you initialize it with this
command:

```bash
source venv/bin/activate
```

If you don't, you will probably have problems running the
Django commonds.

### Get the source

```bash
git clone <repository-name>
# We need a command here that will fetch submodules
```

This includes both the server, and a reference
implementation of on Tutoron: Python.  This Tutoron is
currently needed for checking some of the logic of
successful requests (though we might phase it out later).

### Install the dependencies

This tutorial assumes you are using Python 2.7.

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Set up the local database

```bash
DJANGO_SETTINGS_MODULE=tutorons.settings.dev \
  python manage.py migrate
```

### Test the core

This command will run tests for the Tutorons core as well as
all additional installed modules.

```bash
./runtests.sh
```

### Start the server

Run this command, and then see that the server is running by
going to `http://localhost:8002`.

```bash
./rundevserver.sh
```

A port number can be provided as an argument to
`rundevserver.sh` if you want to run the server on a
different port.

## Building a Java API Annotator

### Creating a new submodule

First, create a new repository.  Then, link it as a
submodule in the `modules` directory.

```bash
cd tutorons/modules/
git submodule add \
  https://github.com/andrewhead/Tutorons-Java-Classes \
  java_classes
```

### Writing tests

### Create views

Add two URLs: One for the base, one to include scan and
explain.

### Implementing `pagescan`

### Adding an endpoint to the JavaScript loader

## More information

A fuller version of the Tutorons server with support for
explaining `wget` command lines, CSS selectors, and regular
expressions, is posted in the
[tutorons-server](https://github.com/andrewhead/tutorons-server)
repository.  You may want to refer to it for more advanced
code detection and explanation patterns.
