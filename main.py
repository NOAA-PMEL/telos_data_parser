import csv
import re
from dateutil import parser
from datetime import timedelta
import dearpygui.dearpygui as dpg
import os

import_path = f'D:\Data\TELOS Parsing\\07262022.TXT'
export_path = f'D:\Data\TELOS Parsing'

'''
TODO:
    Check import and export things
    Creat some sort of text log output for errors and stats.
'''

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

def GUI():

    dpg.create_context()

    def check_export():

        if os.path.isfile(dpg.get_value('input_file')):

            data, date, errors = read_and_parse(import_path)
            write_files_and_folders(export_path, data, date)

            dpg.set_value('report', f'Exported. \n {errors}')

        else:

            dpg.set_value('report', 'Set input filepath!')


    def get_file_path():
        file_uid = dpg.generate_uuid()

        with dpg.file_dialog(label='File Dialog', width=500, height=400, show=False, tag=file_uid,
                             default_path=os.path.abspath(os.path.curdir),
                             callback=lambda s, a, u: dpg.set_value('input_file', list(a['selections'].values())[0])):
            dpg.add_file_extension('.*')
            dpg.add_file_extension('')
            dpg.add_file_extension('.txt')

        dpg.show_item(file_uid)

    def get_folder_path():
        folder_uid = dpg.generate_uuid()

        with dpg.file_dialog(label='Folder Dialog', width=500, height=400, show=False, tag=folder_uid,
                             default_path=os.path.abspath(os.path.curdir), directory_selector=True,
                             callback=lambda s, a, u: dpg.set_value('export_path', a['file_path_name'])):
            dpg.add_file_extension('.*')
            dpg.add_file_extension('')
            dpg.add_file_extension('.txt')

        dpg.show_item(folder_uid)

    with dpg.window(tag='primary'):

        with dpg.group(horizontal=True):
            dpg.add_input_text(tag='input_file', label='', width=400)
            dpg.add_button(tag='get_import_path', label='Open', callback=get_file_path)

        with dpg.group(horizontal=True):
            dpg.add_input_text(tag='export_path', default_value=os.path.abspath(os.path.curdir), width=400)
            dpg.add_button(tag='get_export_path', label='Open', callback=get_folder_path)

        dpg.add_button(tag='export', label='Parse and Export', callback=check_export)

        dpg.add_text(tag='report')
        dpg.add_

    dpg.create_viewport(title='TELOS Data Parsing', width=600, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window('primary', True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':

    GUI()
    # data, date, errors = read_and_parse(import_path)
    # print(errors)
    # write_files_and_folders(export_path, data, date)