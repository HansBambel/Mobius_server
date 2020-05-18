import requests
import os


def download_files(server, api_key, download_folder="downloaded_files"):
    files_response = requests.get(server, headers={"API-key": api_key})
    if files_response.status_code != 200:
        print("Something went wrong with a connection to the server.")
    else:
        # Put the files in a list
        files = [f for f in files_response.json()]
        print(files)
    # Now download every single file
    print(f"Found {len(files)} files to download.")
    for file_name in files:
        data_resp = requests.get(server + "/" + file_name, headers={"API-key": api_key})
        if data_resp.status_code == 200:
            # Save file
            os.makedirs(download_folder, exist_ok=True)
            with open(os.path.join(download_folder, file_name), "wb") as f:
                f.write(data_resp.content)
        else:
            print(f"Something went wrong with downloading with the file {file_name}")


if __name__ == "__main__":
    server_address = "http://127.0.0.1:5000"
    save_files_to = "downloaded_files"
    download_files(server=f"{server_address}/files", api_key="<API-key>", download_folder=save_files_to)