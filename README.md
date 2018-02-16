# AWS DynamoDB Helper

### How to Use

 1. Clone / fork this repo
 2. Copy the `aws_dynamodb_helper.py` file into your project
 3. Simply `from aws_dynamodb_helper import DynamoDBTable`

**NOTE: AWS DynamoDB Helper requires you to have an AWS account, have `boto3` installed, and have performed the basic configuration detailed [here](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration).**

**ALSO: The current version of AWS DynamoDB Helper only support interactions with already created DynamoDB tables. Adding support for table creation / deletion is a top priority for future releases.**

### Examples


```python
from aws_dynamodb_helper import DynamoDBTable
```

**Connect to and Inspect a Table**
```python
table = DynamoDBTable("Fake_Users_Table")

num_items = len(table)
print("# Items in Table:", num_items)

print("Items in Table:", table.list_items(num_items))
```

    # Items in Table: 5
    Items in Table: ['admin', 'other_user2', 'other_user3', 'other_user', 'me']



```python
"other_user3" in table
```




    True




```python
"other_user4" in table
```




    False



**Inspect an Item / Entry in that Table**
```python
print(type(table["other_user3"]))
table["other_user3"]
```

    <class 'aws_dynamodb_helper.DynamoDBTableItem'>





    {'username': {'S': 'other_user3'}, 'password': {'S': 'still_not_me'}}




```python
table["other_user3"].keys()
```




    ['username', 'password']




```python
table["other_user3"].values()
```




    ['other_user3', 'still_not_me']




```python
table["other_user3"].items()
```




    [('username', 'other_user3'), ('password', 'still_not_me')]




```python
"password" in table["other_user3"]
```




    True




```python
"birthday" in table["other_user3"]
```




    False




```python
table["other_user3"]["password"]
```




    'still_not_me'



**Edit an Attribute of that Item**
```python
table["other_user3"]["password"] += "!"
table["other_user3"]["password"]
```




    'still_not_me!'



**Delete an Attribute of that Item**
```python
del table["other_user3"]["password"]
table["other_user3"]["password"]
```


    ---------------------------------------------------------------------------

    KeyError                                  Traceback (most recent call last)

    <ipython-input-19-942006c52e5d> in <module>()
          1 del table["other_user3"]["password"]
    ----> 2 table["other_user3"]["password"]


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __getitem__(self, item)
         99
        100     def __getitem__(self, item):
    --> 101         attribute = DynamoDBTableItemAttribute(self.raw[item])
        102         return attribute.value
        103


    KeyError: 'password'



```python
table["other_user3"]
```




    {'username': {'S': 'other_user3'}}



**Add an Attribute to that Item**
```python
table["other_user3"]["password"] = "still_not_me"
table["other_user3"]
```




    {'username': {'S': 'other_user3'}, 'password': {'S': 'still_not_me'}}



**Delete an Item / Entry from the Table**
```python
del table["other_user3"]
"other_user3" in table
```




    False



**Add an Item / Entry to the Table**
```python
table["other_user3"]["password"] = "still_not_me"
```


    ---------------------------------------------------------------------------

    KeyError                                  Traceback (most recent call last)

    <ipython-input-23-f8b3a3035770> in <module>()
    ----> 1 table["other_user3"]["password"] = "still_not_me"


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __getitem__(self, item)
        183             return DynamoDBTableItem(self, result["Item"])
        184         else:
    --> 185             raise KeyError(item)
        186
        187     def __setitem__(self, item, value):


    KeyError: 'other_user3'


__*NOTE: The Item / Entry Must be Initialized First*__
```python
table["other_user3"] = {}
table["other_user3"]
```




    {'username': {'S': 'other_user3'}}



*Then you can add attributes like normal*
```python
table["other_user3"]["password"] = "still_not_me"
table["other_user3"]["birthday"] = "???"
table["other_user3"]
```




    {'username': {'S': 'other_user3'}, 'password': {'S': 'still_not_me'}, 'birthday': {'S': '???'}}



**Adding More Complex Attributes**
*NOTE: DynamoDB only supports string, number, boolean, and set type objects.*
```python
table["other_user3"]["favorite_numbers"] = [2, 4, 8]
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-26-ebc66c592c24> in <module>()
    ----> 1 table["other_user3"]["favorite_numbers"] = [2, 4, 8]


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __setitem__(self, item, value)
        105         key_item = self.__getitem__(self.parent_table.key)
        106
    --> 107         type_, value = self.__value_to_type(value)
        108
        109         self.parent_table.dynamodb.update_item(


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __value_to_type(self, value)
         91                             + f"{type(value)}.\n\n"
         92                             + "DynamoDB only supports string, number, boolean, "
    ---> 93                             + "and set type objects.")
         94
         95         return type_, value


    Exception: Your object is of an upsupported type: <class 'list'>.

    DynamoDB only supports string, number, boolean, and set type objects.



```python
table["other_user3"]["favorite_numbers"] = set([2, 4, 8])

print(table["other_user3"]["favorite_numbers"])
print(4 in table["other_user3"]["favorite_numbers"])
print(5 in table["other_user3"]["favorite_numbers"])
```

    {8, 2, 4}
    True
    False


**Different Types of Sets**
```python
table["other_user3"]["favorite_numbers"] = set([2, 4.1, 8])
table["other_user3"]["favorite_numbers"]
```




    {2, 4.1, 8}




```python
table["other_user3"]["favorite_numbers"] = set(["2", "4", "8"])
table["other_user3"]["favorite_numbers"]
```




    {'2', '4', '8'}



**Sets Can Only Contain a Single Data Type**
```python
table["other_user3"]["favorite_numbers"] = set([2, "4", 8])
table["other_user3"]["favorite_numbers"]
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-30-40e0e0427715> in <module>()
    ----> 1 table["other_user3"]["favorite_numbers"] = set([2, "4", 8])
          2 table["other_user3"]["favorite_numbers"]


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __setitem__(self, item, value)
        105         key_item = self.__getitem__(self.parent_table.key)
        106
    --> 107         type_, value = self.__value_to_type(value)
        108
        109         self.parent_table.dynamodb.update_item(


    ~/Github/Original/AWS_DynamoDB_Helper/aws_dynamodb_helper.py in __value_to_type(self, value)
         83                                 + "be the same type.\n\n"
         84                                 + "Your set has the following types: "
    ---> 85                                 + f"{type_counter}")
         86
         87             # DynamoDB expects sets to be passed in as a tuple/list of strings


    Exception: DynamoDB requires that all items in your set be the same type.

    Your set has the following types: Counter({<class 'int'>: 2, <class 'str'>: 1})
