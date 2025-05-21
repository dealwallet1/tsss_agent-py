### Python SDK
```sh
Virtual Environment. : python -m venv venv
Activate the Virtual Environment : venv\Scripts\activate
requirements : pip install -r requirements.txt
```
### poetry
```sh
pip install poetry
cd tsss_agent-py
poetry lock
poetry install
```
Rename env.sample to .env

## Run the CS agent server:

```sh
poetry run agent_server
```