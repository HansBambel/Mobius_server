# Mobius-server
#### Running the server:
1. Setting up flask app in terminal:
    - In Windows: `set FLASK_APP=server.py`
    - In Linux: `export FLASK_APP=server.py`
2. To run the server: `flask run`

**Note:** if run on an Azure instance for example the application will be killed when you close the ssh connection. Instead use `tmux`:
1. Start a tmux session: `tmux`
2. Do the steps from above here
3. Exit the `tmux` window by pressing `ctrl`+`b` and then `d` (detach)
4. To enter a running tmux session: `tmux attach`
5. To close it: go into the session and write `exit`
 
 Optional: 
 - to run flask app in debug mode `set FLASK_DEBUG=1` or `export FLASK_DEBUG=1` before running the server.
 - if `LOGFILE` is specified in `.env` the logger will write to that file.
 - if `UPLOAD_DIRECTORY` in `.env` is not specified it will default to `api_uploaded_files`
 
 #### Usage
 - List uploaded files (No authentication required): GET request to `<server-ip>/files`
 - Upload files: POST request to `<server-ip>/files/<file-name-with-extension>` with allowed `API-key` in header (file may be renamed due to `secure_filename()`-function from flask) and file as attachment
 - Download files: GET request to `<server-ip>/files/<file-name-with-extension>` with allowed `API-key` in header
 
 #### About
 Uploading and downloading is only possible when the user gives an API-key that is also in the `.env`-file of the server in the `ALLOWED_KEYS`-variable.
 
---
##### Requirements
- flask
- dotenv
