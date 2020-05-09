import json
import os
import time
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd


def read_zips_from_folder(folder_name):
    sessions_folder = [folder_name]
    folder_items = sorted(os.listdir(folder_name))
    zip_files = [sessions_folder[0] + '/' + s for s in folder_items if s.endswith('.zip')]
    return zip_files


def csv2mlt(zipfileName, ignore_files=None):
    sensorFormat = "%Y-%m-%dT%H:%M:%S.%f"
    recordingID = zipfileName.split("_")[-1].replace(".zip", "")
    session_datetime = datetime.strptime(recordingID, "%Y-%m-%dT%H-%M-%S-%f")

    new_s = zipfileName.replace('files/', 'files/converted/').replace('.zip', '_MLT.zip')

    with zipfile.ZipFile(zipfileName) as old_zip, \
            zipfile.ZipFile(new_s, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
        for filename in old_zip.namelist():
            # check whether the current file is in files to ignore
            data_json = {}
            if ignore_files is not None:
                skip = sum([ign_f.lower() in filename.lower() for ign_f in ignore_files]) > 0
                if skip:
                    continue
            if not os.path.isdir(filename):
                x = filename.split("_")
                applicationName = x[-1].replace('.csv', '')

                if '.csv' in filename:
                    with old_zip.open(filename) as f:
                        csv_file = pd.DataFrame(pd.read_csv(f, sep=",", header=0))
                        # Time diff = record date - session_datetime
                        # TODO the hardcoded "0 days" could become a problem
                        csv_file["Time"] = (pd.to_datetime(csv_file['Time'],
                                                           format=sensorFormat) - session_datetime).astype(str).map(
                            lambda x: x.replace('0 days ', '')[:-6])
                        if applicationName == 'selfreport':
                            # start = where selfreport == True
                            # end = where selfreport == False
                            new_df = pd.DataFrame()
                            end_idx = np.where(csv_file["Status"] == False)[0]

                            new_df["start"] = csv_file["Time"].iloc[end_idx - 1].values
                            new_df["end"] = csv_file["Time"].iloc[end_idx].values
                            new_df["annotations"] = csv_file.iloc[end_idx]["Transportation_Mode"].values
                            # Make a dictionary from the Transportation_values
                            new_df["annotations"] = new_df["annotations"].apply(lambda x: {"Transportation_Mode": x})
                            csv_file = new_df
                            # print(csv_file)

                        else:
                            # Sensor files (gps and sensors)
                            csv_file.rename(columns={"Time": "frameStamp"}, inplace=True)
                            # csv_file["frameAttributes"] =
                            csv_file = csv_file.groupby('frameStamp').apply(
                                lambda x: x.drop(['frameStamp'], axis=1).to_dict('r')[0]).reset_index(
                                name='frameAttributes')

                        frameUpdates = csv_file.to_json(orient="records", index=True)
                        data_json['recordingID'] = recordingID
                        data_json['applicationName'] = applicationName
                        if applicationName == 'selfreport':
                            data_json['intervals'] = json.loads(frameUpdates.replace("}\n{", "},\n{"))
                        else:
                            data_json['frames'] = json.loads(frameUpdates.replace("}\n{", "},\n{"))
                        new_zip.writestr(filename.replace(".csv", ".json"), json.dumps(data_json, indent=4))


if __name__ == "__main__":
    folder = "files"
    os.makedirs(folder + '/converted', exist_ok=True)
    ignore_files = None

    sessions = read_zips_from_folder(folder)
    if len(sessions) <= 0:
        raise FileNotFoundError(f"No recording sessions found in {folder}")
    # read_data_files(sessions, ignore_files=ignore_files)

    start_time = time.time()
    for zipfileName in sessions:
        # 1. Reading data from zip file
        print("Processing session: " + zipfileName)
        csv2mlt(zipfileName, ignore_files=ignore_files)
        print(f"Processing took {time.time() - start_time:.3f} seconds")
