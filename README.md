# Skribble.io Clone by Noam Genish

## Info
This project uses the (kinda) new "[uv](https://docs.astral.sh/uv/)" package and project manager
it consists of the following packages:
- server - TCP socket based server
- client - pygame client
- shared - a library for mutual functions, classes and consts


## How to run
uv makes it easy!

first make sure [you have uv installed](https://docs.astral.sh/uv/getting-started/installation/)
then open the root project folder and run the commends:
- uv venv - this will install the correct version of python for this project and create a virtual environment for the packages
- uv sync --all-packages

then to run the client/server just type:
uv run [client/server]