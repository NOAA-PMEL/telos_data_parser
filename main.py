import csv
import re
from dateutil import parser
from datetime import timedelta
import os

import_path = f'D:\Data\TELOS Parsing\\07262022.TXT'
export_path = f'D:\Data\TELOS Parsing'

def read_and_parse(path):

    iso_pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')

    cur_inst = f''
    cur_date = f''
    cur_delta = f''
    inst_list = set()
    data_bucket = []
    header_line = 0
    # output_headers = {}

    parsed_data = {}
    error_flags = set()

    # read file
    with open(import_path, 'r') as ifile:
        master_file = ifile.readlines()

    for n, line in enumerate(master_file):

        # skip empty lines
        if len(line) < 2:
            continue

        # skips line containing variables names
        # doesn't work!
        if n == (header_line + 1) and not line.replace(',', '').isnumeric() and (cur_inst != f'0IMM_COMMS'):

            # if cur_inst not in set(parsed_data.keys()):
            #     output_headers[cur_inst] = f'datetime, {line}'
            continue

        # we'll identify new lines when they havem then
        if re.search(iso_pattern, line):

            elems = line.split(',')

            cur_inst = elems[0]
            cur_date = parser.parse(elems[1])
            cur_date = cur_date.replace(tzinfo=None)
            dt = parser.parse(elems[2]).time()
            cur_delta = timedelta(hours=dt.hour, minutes=dt.hour, seconds=dt.second, microseconds=dt.microsecond)
            header_line = n

            if (cur_inst not in set(parsed_data.keys())) and (data_bucket != []):
                parsed_data[cur_inst] = data_bucket
            elif data_bucket != []:
                parsed_data[cur_inst] = parsed_data[cur_inst] + data_bucket

            data_bucket = []
            inst_list.add(cur_inst)     # might be unecessary now

        elif (cur_inst == f'') or (cur_date == f'') or (cur_delta == f''):
            error_flags.add(f'Badly formatted header at {n}')
            continue
        elif cur_inst == '0IMM_COMMS':
            data_bucket.append(f'{cur_date},{line.strip(" ")}')
            continue
        else:
            dn = n - (header_line + 1)
            data_bucket.append(f'{cur_date + dn*cur_delta},{line.strip(" ")}')

    return parsed_data, cur_date, error_flags

def write_files_and_folders(path, data, day):

    for inst in set(data.keys()):

        folder = f'{inst}'
        file_name = f'{day.date()}.csv'
        folder_path = f'{path}\\{folder}'
        write_path = f'{path}\\{folder}\\{file_name}'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(write_path, 'w') as wf:

            for line in data[inst]:
                wf.write(line)


if __name__ == '__main__':

    data, date, errors = read_and_parse(import_path)
    print(errors)
    write_files_and_folders(export_path, data, date)