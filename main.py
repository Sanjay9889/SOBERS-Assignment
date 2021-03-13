import csv
import glob
import json
import os
from datetime import datetime, date

converted_data = []


def read_csv(bank_name, bank_file, bank_spec):
    """
    Read csv file and create a list of data for each file
    :param bank_name: Name of the bank
    :param bank_file: bank file in csv
    :param bank_spec: bank specification
    :return:
    """
    with open(bank_file, encoding="utf-8-sig") as csv_file:
        csv_data = csv.DictReader(csv_file)
        for dict_data in csv_data:
            new_dict = {}
            for field in bank_spec[bank_name]['fields']:
                name = field['name']
                csv_value = dict_data[name]
                new_dict["bank_name"] = bank_name
                try:
                    if field['type'] == 'int':
                        new_dict[name] = int(csv_value)
                    elif field['type'] == 'float':
                        new_dict[name] = float(csv_value)
                    elif field['type'] == 'date':
                        dt_temp = datetime.strptime(csv_value, field['format'])
                        new_dict[name] = date(dt_temp.year,
                                              dt_temp.month,
                                              dt_temp.day)
                    else:
                        new_dict[name] = csv_value
                except:
                    return None
            converted_data.append(new_dict)
    return converted_data


def to_csv_file(bank_data, csv_spec, bank_details, output_file):
    """
    Write converted data to csv file
    """
    with open(output_file, 'w') as csv_file:
        header = []
        bank_name = list(bank_details.keys())[0]
        for field in csv_spec[bank_name]["to_csv"]:
            header.append(field['name'])
        csv_output = csv.writer(csv_file)

        csv_output.writerow(header)

        for bank_name in bank_details.keys():
            for dict_fields in bank_data:
                data_list = []
                if bank_name == dict_fields["bank_name"]:
                    for field in csv_spec[bank_name]["to_csv"]:
                        data_list.append(dict_fields[field['field']])
                    csv_output.writerow(data_list)


def list_all_csv_file(dir):
    """
    Get all csv file and file name
    :param dir: file localtion
    :return: dict of {filename : filpath}
    """
    return {os.path.basename(file).split(".")[0]: file for file in glob.glob(dir + '/*.csv')}


def load_json(json_file):
    with open(json_file) as f:
        data = json.load(f)

    return data


def transform(data, transform_to, bank_name):
    """
    Transform the data to another value
    """
    for data_dict in data:
        if data_dict["bank_name"] == bank_name:
            for rule in transform_to:
                name = rule[1]
                if rule[0] == 'add':
                    data_dict[name] = data_dict[name] + rule[2]
                elif rule[0] == 'add_fields':
                    data_dict[name] = data_dict[name] + data_dict[rule[2]]
                elif rule[0] == 'divide':
                    data_dict[name] = data_dict[name] / rule[2]
                elif rule[0] == 'multiply':
                    data_dict[name] = data_dict[name] * rule[2]
                elif rule[0] == 'subtract':
                    data_dict[name] = data_dict[name] - rule[2]


if __name__ == '__main__':
    bank_details = list_all_csv_file("data")
    bank_specification = "banks.json"
    bank_spec = load_json(bank_specification)
    for bank_name, bank_file in bank_details.items():
        read_csv(bank_name, bank_file, bank_spec)

    for bank_name, bank_file in bank_details.items():
        bank_info = bank_spec.get(bank_name)
        if bank_info and 'transform' in bank_info:
            transform(converted_data, bank_info['transform'], bank_name)

    to_csv_file(converted_data, bank_spec, bank_details, "unified_csv.csv")
