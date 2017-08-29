""" data_model
This class contains helper functions for interacting with an
sqlite3 database using a data model pattern.
Assumes that the class_name passed in to the functions has
member variables whose names match the columns in the database table
"""

def _get_objects_from_db_result(class_name, db_result):
    """
    input: class_name - Class
           db_result -  sqlite3 result from a "select *" type query
    returns: list of Class objects
    """
    args_dict = {}
    cols = _list_columns_from_result(db_result)
    results = db_result.fetchall()
    objects = []
    for result in results:
        for i, val in enumerate(result):
            args_dict[cols[i]] = val
        objects.append(class_name(**args_dict))
    return objects

def _get_vals_from_db_result(db_result):
    """
    input: db_result - sqlite3 result from a select column type query
    returns: list of values
    """
    return list(map(lambda x: x[0], db_result))

def _list_class_attributes(class_name):
    """
    input: class_name - Class
    returns: alphabetically sorted member variables for class_name
    """
    return sorted(class_name().__dict__.keys())

def _list_columns_from_result(result):
    """
    input: result - sqlite3 result from a query
    returns: a list of the names for each column in the result input
             the order of the column names matches the order of the result input
    """
    return list(map(lambda x: x[0], result.description))

def _get_class_vals(obj):
    """
    input: obj - object of type Class
    returns: list of member variable values of obj, sorted alphabetically by
             member variable name
    """
    vals = []
    for attr in sorted(obj.__dict__.keys()):
        vals.append(getattr(obj, attr))
    return vals

# --------------------------------------------------
# Database access functions

def get_objects_from_db(class_name, db):
    """
    input: class_name - Class
           table_name - string of table in database
           db - database
    returns: list of class_name objects in database
    """
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    db_result = cur.execute("SELECT * FROM " + table_name)
    return _get_objects_from_db_result(class_name, db_result)

def get_object_from_db_by_key(class_name, key_name, key_val, db):
    """
    input: class_name - Class
           key_name - string of name of key column
           key_val - value of the key
           db - database
    returns: class_name object that matches the item in the database,
             or None if not found
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ?",
                            (key_val,))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects[0]

def get_objects_from_db_by_key(class_name, key_name, key_val, db):
    """
    input: class_name - Class
           key_name - string of name of key column
           key_val - value of the key
           db - database
    returns: list of class_name object that matches the item in the database,
             or None if not found
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ?",
                            (key_val,))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects

def get_object_from_db_by_2key(class_name, key_name1, key_val1, key_name2, key_val2, db):
    """
    input: class_name - Class
           key_name1 - string of name of first key column
           key_val1 - value of the first key
           key_name2 - string of name of second key column
           key_val2 - value of the second key
           db - database
    returns: class_name object that matches the item in the database,
             or None if not found
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name1 + " = ? " +
                            "AND " + key_name2 + " = ?",
                            (key_val1, key_val2))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects[0]

def get_objects_from_db_by_key_and_col_condition(class_name, key_name, key_val, col_name, col_val, condition, db):
    """
    condition: <, <=, >, >=, =
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ? AND " + col_name + " " + condition  + " ? ORDER BY " + col_name, (key_val,col_val,))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects

def get_objects_from_db_by_key_and_two_col_condition(class_name, key_name, key_val, col1_name, col1_val, condition1, col2_name, col2_val, condition2, db):
    """
    condition: <, <=, >, >=, =
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ? AND " + col1_name + " " + condition1 + " ? AND " + col2_name + " " + condition2 + " ? ORDER BY " + col1_name, (key_val,col1_val,col2_val,))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects

def get_objects_from_db_by_key_sorted(class_name, key_name, key_val, sort_col, db):
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    db_result = cur.execute("SELECT * FROM " + table_name + " where " + key_name + " = ? ORDER BY " + sort_col, (key_val,))
    objects = _get_objects_from_db_result(class_name, db_result)
    if len(objects) == 0:
        return None
    return objects

def get_objects_from_db_sorted(class_name, db, sort_col1, sort_col2=None):
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    db_result = None
    if sort_col2:
        db_result = cur.execute("SELECT * FROM " + table_name + " ORDER BY " + sort_col1 + ", " + sort_col2)
    else:
        db_result = cur.execute("SELECT * FROM " + table_name + " ORDER BY " + sort_col1)
    return _get_objects_from_db_result(class_name, db_result)
    
def insert_object_into_db (obj, db):
    """
    input: obj - object to insert into database
           db - database
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(obj.__class__)
    attr_list = ','.join(_list_class_attributes(obj.__class__))
    val_list = ','.join(list(len(_list_class_attributes(obj.__class__)) * '?'))
    cur.execute("INSERT INTO " + table_name + " (" + attr_list + ") VALUES (" + val_list + ")",
                _get_class_vals(obj))
    db.commit()

def update_column_in_db_by_key (column_name, column_val, key_name, key_val, class_name, db):
    """
    input: column_name - string name of column to update in db
           column_val - value of column
           key_name - string name of the key
           key_val - value of the key
           class_name - string name of the class
           db - database
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(class_name)
    cur.execute("UPDATE " + table_name + " SET " + column_name + "=?" + " WHERE " +
                key_name + "=?", (column_val, key_val))
    db.commit()

def update_object_in_db_by_key (obj, key_name, key_val, db, do_insert=True):
    """
    input: obj - data model object
           key_name - string of the key column name
           key_val - value of the key
           db - database
           do_insert - boolean. if true, object will be inserted if it doesn't exist in the db
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(obj.__class__)
    if get_object_from_db_by_key (obj.__class__, key_name, key_val, db):
        # object exists
        attr_list = _list_class_attributes(obj.__class__)
        set_string = ','.join('%s=?' % t for t in attr_list)
        val_list = _get_class_vals(obj)
        val_list.append(key_val)
        cur.execute("UPDATE " + table_name + " SET " + set_string + " WHERE " + key_name + "=?",
                    val_list)
        db.commit()
    else:
        if do_insert:
            insert_object_into_db(obj, db)

def update_object_in_db_by_2key (obj, key_name1, key_val1, key_name2, key_val2, db, do_insert=True):
    """
    input: obj - data model object
           key_name1 - string of the key1 column name
           key_val1 - value of the key1
           key_name2 - string of the key2 column name
           key_val2 - value of the key2
           db - database
           do_insert - boolean. if true, object will be inserted if it doesn't exist in the db
    """
    cur = db.cursor()
    table_name = class_name_to_table_name(obj.__class__)
    if get_object_from_db_by_2key (obj.__class__, key_name1, key_val1, key_name2, key_val2, db):
        # object exists
        attr_list = _list_class_attributes(obj.__class__)
        set_string = ','.join('%s=?' % t for t in attr_list)
        val_list = _get_class_vals(obj)
        val_list.append(key_val1)
        val_list.append(key_val2)
        cur.execute("UPDATE " + table_name + " SET " + set_string + " WHERE " + key_name1 + "=? " + \
                    " AND " + key_name2 + "=?", val_list)
        db.commit()
    else:
        if do_insert:
            insert_object_into_db(obj, db)

def delete_by_key(class_name, key_name, key_val, db):
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    cur.execute('DELETE FROM ' + table_name + " WHERE " + key_name + "=?", (key_val,))
    db.commit()

def clear_table (class_name, db):
    """
    input: class_name - Class
    returns: nothing
    """
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    cur.execute('DELETE FROM ' + table_name)
    db.commit()

def clear_table_by_key (class_name, key_name, key_val, db):
    """
    input: class_name - Class, key_name - string, key_val - value of key
    returns: nothing
    """
    table_name = class_name.__name__.lower()
    cur = db.cursor()
    cur.execute('DELETE FROM ' + table_name + " where " + key_name + " = ?",
                (key_val,))
    db.commit()

def class_name_to_table_name (class_name):
    """
    input: class_name - Class
    returns: a string of the class with the first letter lowercase
    """
    class_str = class_name.__name__
    if len(class_str) == 0:
        return ''
    elif len(class_str) == 1:
        return class_str.lower()
    return class_str[0].lower() + class_str[1:]

def get_distinct(class_name, column_name, db):
    """
    input: class_name - Class, column_name - string
    returns: a list of unique values contained in the column
    """
    table_name = class_name_to_table_name(class_name)
    cur = db.cursor()
    db_result = cur.execute("SELECT DISTINCT " + column_name + " FROM " + table_name)
    return _get_vals_from_db_result(db_result.fetchall())
