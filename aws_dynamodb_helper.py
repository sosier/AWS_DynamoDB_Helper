import boto3 as aws
from collections import Counter


class DynamoDBTableItemAttribute(object):
    def __init__(self, item):
        self.raw = item
        self.value = self.__raw_to_value()

    def __parse_N_type_item(self, item):
        if "." in item:
            result = float(item)
        else:
            result = int(item)

        return result

    def __correct_raw_item_type(self, type_, item):
        result = item

        if type_ == "S":  # String
            result = str(item)
        elif type_ == "N":  # Number
            result = self.__parse_N_type_item(item)
        elif type_ == "BOOL":  # Boolean
            result = bool(item)
        elif type_ == "B":  # Binary
            result = bin(item)
        elif type_ == "SS":  # String Set
            result = set(str(set_item) for set_item in set(item))
        elif type_ == "NS":  # Number Set
            result = set(self.__parse_N_type_item(set_item)
                         for set_item in set(item))
        elif type_ == "BS":  # Binary Set
            result = set(bin(set_item) for set_item in set(item))

        return result

    def __raw_to_value(self):
        if len(self.raw) == 1:
            value = self.__correct_raw_item_type(*list(self.raw.items())[0])
        else:
            value = [self.__correct_raw_item_type(*list(raw_item.items())[0])
                     for raw_item in self.raw]

        return value


class DynamoDBTableItem(object):
    def __init__(self, parent_table, item):
        self.parent_table = parent_table
        self.raw = item

    def __value_to_type(self, value):

        if type(value) == str:
            type_ = "S"  # String
        elif type(value) in (int, float):
            type_ = "N"  # Number
            value = str(value)
        elif type(value) == bool:
            type_ = "BOOL"  # Boolean
        elif type(value) == set:
            set_item = next(iter(value))

            if type(set_item) == str:
                type_ = "SS"  # String Set
            elif type(set_item) in (int, float):
                type_ = "NS"  # Number Set
            else:
                raise Exception("The set you passed in contains an "
                                + f"unsupported type: {type(set_item)}.\n\n"
                                + "DynamoDB only supports set contents that "
                                + "are strings or numbers.")

            type_counter = Counter(type(item) for item in value)

            if len(type_counter) > 1 and not (
                    len(type_counter) == 2
                    and float in type_counter
                    and int in type_counter):
                raise Exception("DynamoDB requires that all items in your set "
                                + "be the same type.\n\n"
                                + "Your set has the following types: "
                                + f"{type_counter}")

            # DynamoDB expects sets to be passed in as a tuple/list of strings
            value = tuple(str(item) for item in value)
        else:
            raise Exception("Your object is of an unsupported type: "
                            + f"{type(value)}.\n\n"
                            + "DynamoDB only supports string, number, boolean, "
                            + "and set type objects.")

        return type_, value

    def __contains__(self, item):
        return item in self.raw

    def __getitem__(self, item):
        attribute = DynamoDBTableItemAttribute(self.raw[item])
        return attribute.value

    def __setitem__(self, item, value):
        key_item = self.__getitem__(self.parent_table.key)

        type_, value = self.__value_to_type(value)

        self.parent_table.dynamodb.update_item(
            TableName=self.parent_table.table,
            Key={self.parent_table.key: {self.parent_table.key_type: key_item}},
            AttributeUpdates={
                str(item): {
                    "Value": {
                        type_: value
                    },
                    "Action": "PUT"
                }
            }
        )

    def __delitem__(self, item):
        key_item = self.__getitem__(self.parent_table.key)

        self.parent_table.dynamodb.update_item(
            TableName=self.parent_table.table,
            Key={self.parent_table.key: {self.parent_table.key_type: key_item}},
            AttributeUpdates={
                str(item): {"Action": "DELETE"}
            }
        )

    def __repr__(self):
        return str(self.raw)

    def keys(self):
        return list(self.raw.keys())

    def values(self):
        return [DynamoDBTableItemAttribute(value).value for value in self.raw.values()]

    def items(self):
        return list(zip(self.keys(), self.values()))


class DynamoDBTable(object):
    def __init__(self, table):
        self.dynamodb = aws.client("dynamodb")
        self.table = table

        table_details = self.dynamodb.describe_table(TableName=self.table)["Table"]
        key_details = table_details["AttributeDefinitions"]

        if len(key_details) == 1:
            self.multi_key = False
            self.key = key_details[0]["AttributeName"]
            self.key_type = key_details[0]["AttributeType"]
        else:
            raise Exception("Multi-Key tables not currently supported")

    def __len__(self):
        result = self.dynamodb.scan(TableName=self.table,
                                    Select="COUNT")
        return result["Count"]

    def __get(self, item, what=[]):
        if what:
            result = self.dynamodb.get_item(TableName=self.table,
                                            Key={self.key: {self.key_type: item}},
                                            AttributesToGet=what)
        else:
            result = self.dynamodb.get_item(TableName=self.table,
                                            Key={self.key: {self.key_type: item}})

        return result

    def __contains__(self, item):
        return "Item" in self.__get(item, [self.key])

    def __getitem__(self, item):
        result = self.__get(item)
        if "Item" in result:
            return DynamoDBTableItem(self, result["Item"])
        else:
            raise KeyError(item)

    def __setitem__(self, item, value):
        self.dynamodb.update_item(
            TableName=self.table,
            Key={self.key: {self.key_type: item}}
        )

    def __delitem__(self, item):
        self.dynamodb.delete_item(
            TableName=self.table,
            Key={self.key: {self.key_type: item}}
        )

    def list_items(self, limit=100):
        result = self.dynamodb.scan(TableName=self.table,
                                    AttributesToGet=[self.key],
                                    Limit=limit)

        if "Items" not in result:
            return []
        else:
            return [list(item[self.key].values())[0] for item in result["Items"]]
