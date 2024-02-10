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
            time TEXT,
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

        Para:
            table_name - Name of the table to be created.
            columns - List of tuples with the format (column_name, data_type).

        Example:
            >>> columns = [("p", "REAL"), ("i", "REAL"), ("d", "REAL"), ("trial_notes", "TEXT")]
            >>> database.create_user_defined_table("UsersControllerParameters", columns)
        """
        columns_sql = ',\n'.join([f"{name} {data_type}" for name, data_type in columns])
        fk_sql = ",\nFOREIGN KEY (trial_id) REFERENCES ODriveData(trial_id)"
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            UniqueID INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id INTEGER NOT NULL,
            {columns_sql},
            {fk_sql}
        );
        """
        self.execute(sql)



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




# Example usage
database = OdriveDatabase('odrive_database.db')

# Create user-defined table
columns = [
            ("p", "REAL"),
            ("i", "REAL"),
            ("d", "REAL"),
            ("trial_notes", "TEXT")
            ]
database.create_user_defined_table("UsersControllerParameters", columns)

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
