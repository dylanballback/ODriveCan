from sqlite3 import Error
import sqlite3



class OdriveDatabase:
    def __init__(self, database_path=None):
        """
        Initializes the database connection.

        Para:
            database_path - Path to the SQLite database file. If None, defaults to 'odrive.db' in the current working directory.

        Example:
            >>> database = OdriveDatabase('odrive_database.db')
        """
        if database_path is None:
            database_path = 'odrive.db'
        self.database_path = database_path
        self.conn = self.create_connection()
        self.ensure_odrive_table()  # Ensure the table is created



    def execute(self, sql, params=None):
        """
        Executes a SQL statement.

        Para:
            sql - SQL query to be executed.
            params - Optional parameters for the SQL query.

        Returns:
            The row ID of the last row this INSERT modified, or None on failure.

        Example:
            >>> database.execute("INSERT INTO ODriveData (trial_id) VALUES (?)", (1,))
            ... 
            ... 1
        """
        try:
            c = self.conn.cursor()
            c.execute(sql, params or ())
            self.conn.commit()
            return c.lastrowid
        except Error as e:
            print(e)
            return None



    def create_connection(self):
        """
        Creates a database connection to the SQLite database specified by the database_path.

        Returns:
            Connection object to the SQLite database.

        Example:
            >>> conn = database.create_connection()
        """
        try:
            return sqlite3.connect(self.database_path)
        except Error as e:
            print(e)



    def ensure_odrive_table(self):
        """
        Ensures the ODriveData table exists; creates it if it does not.

        Example:
            >>> database.ensure_odrive_table()
        """
        sql = """
        CREATE TABLE IF NOT EXISTS ODriveData (
            UniqueID INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id INTEGER NOT NULL,
            node_ID TEXT,
            time REAL,
            position REAL,
            velocity REAL,
            torque_target REAL,
            torque_estimate REAL,
            bus_voltage REAL,
            bus_current REAL,
            iq_setpoint REAL,
            iq_measured REAL,
            electrical_power REAL,
            mechanical_power REAL
        );
        """
        self.execute(sql)



    def create_user_defined_table(self, table_name, columns):
        """
        Creates a user-defined table with specified columns and foreign key relationship to the O-Drive Data table.

        Params:
            table_name - Name of the table to be created.
            columns - List of tuples with the format (column_name, data_type).

        Example:
            >>> columns = [("p", "REAL"), ("i", "REAL"), ("d", "REAL"), ("trial_notes", "TEXT")]
            >>> database.create_user_defined_table("UsersControllerParameters", columns)
        """
        # Join the column definitions into a single string
        columns_sql = ',\n'.join([f"{name} {data_type}" for name, data_type in columns])

        # Define the foreign key SQL, ensuring no leading comma
        fk_sql = "FOREIGN KEY (trial_id) REFERENCES ODriveData(trial_id)"

        # Combine column definitions and foreign key clause, ensuring no extraneous commas
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            UniqueID INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id INTEGER NOT NULL,
            {columns_sql},
            {fk_sql}
        );
        """
        #print(sql)
        # Execute the SQL statement
        self.execute(sql)


    def insert_into_user_defined_table(self, table_name, columns, values):
        """
        Inserts data into a user-defined table after validating data types. Ensures foreign key constraints are respected.

        Params:
            table_name - Name of the table where data will be inserted.
            columns - List of column names where the data needs to be inserted.
            values - List of values corresponding to the columns.
        """
        # Assuming validation includes foreign key existence checks or is handled externally
        if self.validate_data_types(table_name, dict(zip(columns, values))):
            columns_sql = ', '.join(columns)
            placeholders = ', '.join(['?' for _ in values])
            sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
            self.execute(sql, values)
        else:
            print("Data type validation failed. No data inserted.")


#----------- Methods to validate that data being uploaded to user defined table is correct type. -----------------

    def validate_data_types(self, table_name, insert_data):
        """
        Validates the datatypes of the insert_data against the expected datatypes of the columns in the table.

        Params:
            table_name - Name of the table where data will be inserted.
            insert_data - Dictionary with the format {column_name: value} for the data to be inserted.
        """
        expected_data_types = self.get_expected_column_types(table_name)
        for column, value in insert_data.items():
            expected_type = expected_data_types.get(column)
            if not self.check_data_type(value, expected_type):
                print(f"Value for column '{column}' does not match expected type '{expected_type}'.")
                return False
        return True

    def fetch(self, sql, params=None):
        """
        Fetches data from the database using a SQL statement.

        Params:
            sql - SQL query to be executed.
            params - Optional parameters for the SQL query.

        Returns:
            A list of rows returned by the query.
        """
        try:
            c = self.conn.cursor()
            c.execute(sql, params or ())
            return c.fetchall()  # Fetch and return all rows
        except Error as e:
            print(e)
            return []

    def get_expected_column_types(self, table_name):
        """
        Retrieves the expected column types for a given table.

        Params:
            table_name - Name of the table.
        """
        sql = f"PRAGMA table_info({table_name});"
        rows = self.fetch(sql)  # Use fetch instead of execute
        return {row[1]: row[2] for row in rows}


    def check_data_type(self, value, expected_type):
        """
        Checks if a value matches the expected SQLite data type.

        Params:
            value - The value to check.
            expected_type - The expected SQLite data type as a string.
        """
        type_map = {
            'INTEGER': int,
            'REAL': (int, float),
            'TEXT': str,
            # Add more mappings as necessary
        }
        return isinstance(value, type_map.get(expected_type, object))

    

#-----------------------------------------------------------------------------------------------------------

    def get_next_trial_id(self):
        """
        Fetches the next trial_id by finding the maximum trial_id in the database and adding 1.

        Returns:
            The next trial_id to be used.
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT MAX(trial_id) FROM ODriveData")
            max_id = c.fetchone()[0]
            if max_id is not None:
                return max_id + 1
            else:
                return 1  # If table is empty, start with 1
        except Error as e:
            print(e)
            return 1  # Default to 1 if there's an issue



    def add_odrive_data(self, trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power):
        """
        Inserts data into the ODriveData table.

        Para:
            trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power - Fields representing the data to be inserted into the ODriveData table.

        Returns:
            The row ID of the last row this INSERT modified, or None on failure.

        Example:
            >>> database.add_odrive_data(1, 'node_1', '2024-02-09 10:00:00', 123.45, 67.89, 2.34, 2.30, 48.0, 1.5, 3.33, 3.30, 120, 110)
            ...
            ... 1
        """
        sql = '''INSERT INTO ODriveData(trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power)
                 VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
        return self.execute(sql, (trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power))


    def bulk_insert_odrive_data(self, data_list):
        """Inserts multiple data records into the database."""
        conn = self.create_connection()  # Create a new connection
        try:
            c = conn.cursor()
            for data in data_list:
                sql = '''INSERT INTO ODriveData(trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power)
                         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
                params = (data['trial_id'], data['node_ID'], data['time'], data['position'], data['velocity'], data['torque_target'], data['torque_estimate'], data['bus_voltage'], data['bus_current'], data['iq_setpoint'], data['iq_measured'], data['electrical_power'], data['mechanical_power'])
                c.execute(sql, params)
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()




"""
# Example usage


database = OdriveDatabase('odrive_database.db')

# Define columns for the new table
columns = [
    ("kp", "REAL"),
    ("ki", "REAL"),
    ("kd", "REAL"),
    ("remarks", "TEXT"),
    ("trial_id", "INTEGER"),  # Assuming you want to keep a foreign key relationship
]

# Create the table
database.create_user_defined_table("TestParameters", columns)


# Define the table name, columns, and values for the new record
table_name = "TestParameters"
columns = ["kp", "ki", "kd", "remarks", "trial_id"]
values = [0.5, 0.00, 0.01, "Initial test parameters", 1]  # Ensure trial_id 1 exists in ODriveData

# Insert the data
database.insert_into_user_defined_table(table_name, columns, values)



# Add O-Drive Data
trial_id = 1
node_ID = 0
time = '2024-02-09 10:00:00'
position = 123.45
velocity = 67.89
torque_target = 2.34
torque_estimate = 2.30
bus_voltage = 48.0
bus_current = 1.5
iq_setpoint = 3.33
iq_measured = 3.30
electrical_power = 120
mechanical_power = 110

database.add_odrive_data(trial_id, node_ID, time, position, velocity, torque_target, torque_estimate, bus_voltage, bus_current, iq_setpoint, iq_measured, electrical_power, mechanical_power)
"""
