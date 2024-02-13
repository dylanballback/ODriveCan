## Create a custom user defined table and add data to it. 

### Simple Example: 

This is an example of how to create your own table inside the database to store custom data.


In this example I am creating a new table called `pid_parameters` and adding the columns `kp`, `ki`, `kd`, and `remarks`. 


I will be using this table to keep track of my PID constants set for each trial along with any additional comments/remarks I want to add. 


The `trial_id` will automatically be added to the table as a foreign key to link this data to its corresoponding data in the `ODriveData` table. 


```python 
import pyodrivecan

database = pyodrivecan.OdriveDatabase('odrive_database.db')

# Define the table name
table_name = "pid_parameters"

# Define columns and SQL datatypes for the new table
columns = [
    ("kp", "REAL"),
    ("ki", "REAL"),
    ("kd", "REAL"),
    ("remarks", "TEXT")
]

# Create the table
database.create_user_defined_table(table_name, columns)

# Define the existing columns, and values for the new record
columns = ["trial_id", "kp", "ki", "kd", "remarks", ]
values = [1, 0.5, 0.00, 0.01, "Initial test parameters"]  # Ensure trial_id 1 exists in ODriveData

# Insert the data from the 'values' list above
database.insert_into_user_defined_table(table_name, columns, values)
```

#### Results:

![User Defined Table Example Results](media/databaseMedia/ODriveCAN_example_database.png)

As you can see in the image above, the package will automatically handle setting up the 
trial_id as your foriegn key to link the data between the ODriveData table and your custom user defined table. 
