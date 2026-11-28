# Timeit

timeit is a simple tool for tracking work time.

## Installation

Clone the repository and run the installation script.
For now the app can only be installed with root privileges.
Note: the app does not need to be installed to be run (see building and developmen)

```sh
git clone https://github.com/nilsrobinet/timeit.git
cd timeit
./install.sh
```

after that the app is installed and should be listening on port 8080

## Building and Development

The frontend of the app is written in vue.js.

To build it the following steps can be followed:

```sh

cd frontend
npm install
npm run build

```

To run the server a few requirements are necessary. It is recommended to install them in a virtual environment:

```sh

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements

```
