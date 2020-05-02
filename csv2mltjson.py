import numpy as np
import zipfile, os, json, re, datetime, time
import csv
import pandas as pd
from datetime import datetime
import pickle

folder = "files"
if not os.path.exists(folder + '/converted'):
    os.makedirs(folder + '/converted')
ignore_files = []


def read_zips_from_folder(folder_name):
    sessions_folder = [folder_name]
    folder_items = sorted(os.listdir(folder_name))
    zip_files = [sessions_folder[0] + '/' + s for s in folder_items if s.endswith('.zip')]
    return zip_files


def parseDateTimeFromFileName(filename):
    x = filename.split("_")
    x = x[len(x) - 1].replace('.zip', '').replace('T', '-')

    return x


sessions = read_zips_from_folder(folder)
if len(sessions) <= 0:
    raise FileNotFoundError(f"No recording sessions found in {folder}")
# read_data_files(sessions, ignore_files=ignore_files)


# def csv2mltjson():
for s in sessions:
    # 1. Reading data from zip file
    print("Processing session: " + s)
    recordingID = parseDateTimeFromFileName(s)
    session_datetime = datetime.strptime(recordingID, "%Y-%m-%d-%H:%M:%S.%f")
    new_s = s.replace('files/', 'files/converted/').replace('.zip', '_MLT.zip')

    with zipfile.ZipFile(s) as old_zip, \
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
                applicationName = x[len(x) - 1].replace('.csv', '')

                if '.csv' in filename:
                    with old_zip.open(filename) as f:
                        data = csv.DictReader(f)
                        csv_file = pd.DataFrame(pd.read_csv(f, sep=",", index_col=False)).rename(
                            columns=lambda x: x.strip())
                        # csv_file.set_index('Time',inplace=True)
                        csv_file = csv_file.groupby('Time').apply(
                            lambda x: x.drop(['Time'], axis=1).to_dict('r')[0]).reset_index(
                            name='frameAttributes').rename(columns={"Time": "frameStamp"})

                        csv_file['frameStamp'] = (pd.to_datetime(csv_file['frameStamp'],
                                                                 format="%Y-%m-%dT%H:%M:%S.%f") - session_datetime).astype(
                            str).map(lambda x: x.replace('0 days ','')[:-6])
                        frameUpdates = csv_file.to_json(orient="records", index=True)
                        data_json['recordingID'] = recordingID
                        data_json['applicationName'] = applicationName
                        data_json['frames'] = json.loads(frameUpdates.replace("}\n{", "},\n{"))
                        new_zip.writestr(filename.replace(".csv", ".json"), json.dumps(data_json, indent=4))
