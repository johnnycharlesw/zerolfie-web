import os_getter
import os
import sys
import sqlite3

def find_or_create_data_folder():
    # Determine the appropriate folder location based on the operating system
    if os_getter.os_name == "Windows":
        folder_name = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\ZerolfieWeb"  # Windows
    else:
        folder_name = os.path.join(os.path.expanduser("~"), ".zerolfie-web")  # Linux/Mac

    os.makedirs(folder_name, exist_ok=True)  # Create directory if it does not exist

    return folder_name

class Profile:
    def __init__(self, name):
        self.name = name
        self.datafolder = os.path.join(find_or_create_data_folder(), f"profile_{name}/")
        os.makedirs(self.datafolder, exist_ok=True)  # Create profile folder if it does not exist

        # Initialize the SQLite database
        self.mydb = sqlite3.connect(os.path.join(self.datafolder, f"default.db"))  # Database file in profile folder
        self.cursor = self.mydb.cursor()

        # Update the schema or create the profile
        self.update_schema()

    def does_table_exist(self, table):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        table = self.cursor.fetchone()
        exists = table is not None
        return exists

    def was_schema_applied(self):
        tables = self.get_tables()
        applied_tables = []
        for table in tables:
            if self.does_table_exist(table):
                applied_tables+=table
        return tables == applied_tables


    def create_this_profile(self):
        if not self.was_schema_applied():
            self._create_this_profile()

    def _create_this_profile(self):
        """Apply all SQL schema files from the 'sql' folder to the database."""
        sql_folder = os.path.join(os.path.dirname(__file__), 'sql')  # Path to the SQL folder
        
        for filename in os.listdir(sql_folder):
            if filename.endswith('.sql'):
                with open(os.path.join(sql_folder, filename), 'r') as file:
                    sql_script = file.read()
                    try:
                        self.cursor.executescript(sql_script)  # Execute the SQL script
                        self.mydb.commit()  # Commit the changes
                    except sqlite3.Error as e:
                        print(f"An error occurred while executing {filename}: {e}")
    
    def _is_table_compatible_with_schema(self, table):
        """
        Parse a CREATE TABLE SQL statement and return a dictionary of column names and types.

        Args:
            create_table_sql (str): The CREATE TABLE SQL statement.

        Returns:
            dict: A dictionary where keys are column names and values are their types.
        """
        # Regex to match column definitions: `column_name type ...`
        create_table_fd = open(os.path.join(os.path.dirname(__file__), 'sql', table+".sql"))
        create_table_sql=create_table_fd.readlines().join('\n')
        create_table_fd.close()
        pattern = r'`([^`]+)`\s+([^,]+)(?:\([^)]*\))?(?:[^,]*)'
        matches = re.findall(pattern, create_table_sql, re.IGNORECASE)

        schema = {}
        for column, col_type in matches:
            # Clean up the type (remove constraints like NOT NULL, PRIMARY KEY, etc.)
            col_type = re.sub(r'\s.*', '', col_type.strip(), flags=re.IGNORECASE)
            schema[column] = col_type

        return schema
    
    def get_tables(self):
        tables_fd = open(os.path.join(os.path.dirname(__file__), "sql", "tables.txt"))
        tables = tables_fd.readlines()
        tables_fd.close()
        return tables

    def is_table_compatible_with_schema(self, table):
        # get the schema
        schema = _is_table_compatible_with_schema(table)

        # Get the current schema of the table
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        current_columns = {row[1]: row[2] for row in cursor.fetchall()}  # {column_name: column_type}

        # Compare with the expected schema
        for column, expected_type in expected_schema.items():
            if column not in current_columns:
                return False  # Column missing
            if current_columns[column].upper() != expected_type.upper():
                return False  # Column type mismatch

        
        return True


    def update_schema(self):
        if not self.was_schema_applied():
            self.create_this_profile()
        self._update_schema()
    
    def _update_schema(self):
        """Apply all SQL schema files from the 'sql/migrations' folder to the database."""
        sql_folder = os.path.join(os.path.dirname(__file__), 'sql', "migrations")  # Path to the SQL folder
        tables = self.get_tables()
        for table in tables:
            for filename in os.listdir(sql_folder):
                if filename.endswith('.sql') and filename.startswith(table+"-"):
                    with open(os.path.join(sql_folder, filename), 'r') as file:
                        sql_script = file.read()
                        try:
                            self.cursor.executescript(sql_script)  # Execute the SQL script
                            self.mydb.commit()  # Commit the changes
                        except sqlite3.Error as e:
                            print(f"An error occurred while executing {filename}: {e}")
        
    def close(self):
        """Close the database connection."""
        self.mydb.close()

# Example usage
if __name__ == "__main__":
    profile_name = "default"  # Change to your desired profile name
    my_profile = Profile(profile_name)
    my_profile.close()
