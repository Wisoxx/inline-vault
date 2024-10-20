import sqlite3
import os
import time

from logger import setup_logger

MAX_RETRIES = 3
INITIAL_DELAY = 0.5

logger = setup_logger(__name__)


class Connection:
    def __init__(self, database_name, timeout):
        db_path = os.path.expanduser(f"~/mysite/{database_name}")
        logger.info(f"Connecting to database at {db_path}...")
        self.connection = sqlite3.connect(db_path, timeout=timeout)
        self.connection.execute('PRAGMA foreign_keys=ON')

    def __del__(self):
        logger.info("Disconnecting from database...")
        self.connection.close()

    def __getattr__(self, name):
        return getattr(self.connection, name)


class Database:
    table_name = ""
    create_table_query = ""
    columns = ()

    connection = Connection('data.db', timeout=5)

    @classmethod
    def execute_query(cls, query: str, params: list or tuple = (), retrying: bool = False):
        """Executes a given SQLite query with optional parameters. Returns number of affected rows or fetched data"""
        logger.debug(f"Executing query: {query, params}")
        connection = cls.connection
        cursor = connection.cursor()

        attempt = 0
        while attempt < MAX_RETRIES:
            # execute query
            try:
                if params:
                    cursor.execute(query, tuple(params))
                else:
                    cursor.execute(query)

                if not query.strip().upper().startswith("SELECT"):
                    connection.commit()
                    logger.debug(f"Query executed successfully")
                    return cursor
                else:
                    results = cursor.fetchall()  # Return results for SELECT statements
                    logger.debug(f"Query executed successfully. Results: {results}")
                    return results

            # handle errors
            except sqlite3.OperationalError as e:
                error_message = str(e)

                if "database is locked" in error_message:
                    logger.warning(f"Database is locked, retrying... Attempt {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(INITIAL_DELAY * (2 ** attempt))
                    attempt += 1
                    continue

                elif "no such table" in error_message and not retrying:
                    logger.warning(f"Table not found: {cls.table_name}. Attempting to create the table...")
                    try:
                        cls.create_table()  # Attempt to create the table
                        logger.info("Table created successfully. Retrying the original query...")
                    except sqlite3.Error as create_e:
                        logger.critical(f"Failed to create table: {create_e}", exc_info=True)
                        return -1

                    # Retry the original query after creating the table
                    return cls.execute_query(query, params, retrying=True)

                else:
                    logger.exception(f"OperationalError: {error_message}")

            except sqlite3.IntegrityError as e:
                logger.warning(f"IntegrityError: {str(e)}")
                return -1  # Handle duplicate entries and other integrity issues

            except sqlite3.DatabaseError as e:
                logger.critical(f"DatabaseError: {str(e)}", exc_info=True)
                return -1  # Handle other database errors

            finally:
                cursor.close()

        logger.error(f"Max retries exceeded")
        return -1  # Return -1 if all retries fail

    @classmethod
    def validate_columns(cls, conditions: dict or list or tuple) -> None:
        invalid_columns = [col for col in conditions if col not in cls.columns]
        if invalid_columns:
            logger.error(f"Table {cls.table_name} has no such columns: {invalid_columns}")
            raise ValueError(f"Invalid column(s): {', '.join(invalid_columns)}")

    @classmethod
    def create_table(cls) -> None:
        """Create the table specified by class, and create indexes if defined."""
        cls.execute_query(cls.create_table_query)

    @classmethod
    def add(cls, data: dict, replace: bool = False) -> tuple[bool, int]:
        """
        Inserts a new record into the table. Column names and values are passed as a
        dictionary. Optionally, use "INSERT OR REPLACE" to handle unique constraint
        conflicts.

        :param data: dict of data to be inserted
        :param replace: bool whether to replace existing records
        :return: bool indicating success or failure
        """
        if not data:
            raise ValueError("No data provided for insertion.")
        cls.validate_columns(data)

        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))

        if replace:
            query = f"INSERT OR REPLACE INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
        else:
            query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"

        cursor = cls.execute_query(query, data.values())

        return cursor.rowcount > 0, cursor.lastrowid

    @classmethod
    def get(cls, conditions: dict = None, limit: int = None, offset: int = None,
            order_by: str = None, sort_direction: str = 'ASC', include_column_names=False, custom_select=None) -> list or dict or tuple:
        """
        Fetch records from the database with optional conditions, limit, offset, and ordering.

        :param conditions: A dictionary of WHERE conditions (optional)
        :param limit: The maximum number of records to retrieve (optional)
        :param offset: The number of records to skip (optional)
        :param order_by: The column to order by (optional)
        :param sort_direction: 'ASC' or 'DESC' to define sorting direction (default: 'ASC')
        :param include_column_names: Whether to return column names with values (default: False)
        :param custom_select: A custom SELECT query to override the default (optional)
        :return: List of fetched records
        """

        query = custom_select if custom_select else f"SELECT * FROM {cls.table_name}"
        params = []

        # Add WHERE conditions if provided
        if conditions:
            cls.validate_columns(conditions)

            where_clause = ' AND '.join([f"{key} = ?" for key in conditions.keys()])
            query += f" WHERE {where_clause}"
            params.extend(conditions.values())

        # Add ORDER BY if provided
        if order_by:
            if order_by not in cls.columns:
                raise ValueError(f"Invalid column for ordering: {order_by}")
            if sort_direction.upper() not in ['ASC', 'DESC']:
                raise ValueError("Sort direction must be either 'ASC' or 'DESC'")
            query += f" ORDER BY {order_by} {sort_direction.upper()}"

        # Add LIMIT and OFFSET if provided
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        if offset:
            query += " OFFSET ?"
            params.append(offset)

        rows = cls.execute_query(query, params)

        if include_column_names:
            rows = [{cls.columns[i]: row[i] for i in range(len(row))} for row in rows]

        if len(rows) == 1:  # return as tuple instead of list of tuples
            return rows[0]

        return rows

    @classmethod
    def count_where(cls, conditions: dict):
        """Counts the number of records that meet the given conditions."""
        if not conditions:
            raise ValueError("No conditions provided for count.")
        cls.validate_columns(conditions)

        where_clause = ' AND '.join([f"{key} = ?" for key in conditions])
        query = f"SELECT COUNT(*) FROM {cls.table_name} WHERE {where_clause}"
        result = cls.execute_query(query, conditions.values())
        return result[0][0] if result else 0

    @classmethod
    def set(cls, conditions: dict, new_values: dict):
        """Updates records that meet the given conditions with new values."""
        if not conditions:
            raise ValueError("No conditions provided for identifying the row(s).")
        if not new_values:
            raise ValueError("No new values provided for update.")

        cls.validate_columns(conditions)
        cls.validate_columns(new_values)

        set_clause = ', '.join(f"{key} = ?" for key in new_values)
        where_clause = ' AND '.join(f"{key} = ?" for key in conditions)
        query = f"UPDATE {cls.table_name} SET {set_clause} WHERE {where_clause}"
        cursor = cls.execute_query(query, (*new_values.values(), *conditions.values()))
        return cursor.rowcount > 0

    @classmethod
    def delete(cls, conditions: dict):
        """Deletes records that meet the given conditions."""
        if not conditions:
            raise ValueError("No conditions provided for identifying the row(s) to delete.")
        cls.validate_columns(conditions)

        where_clause = ' AND '.join(f"{key} = ?" for key in conditions)
        query = f"DELETE FROM {cls.table_name} WHERE {where_clause}"
        cursor = cls.execute_query(query, tuple(conditions.values()))
        return cursor.rowcount > 0


class Users(Database):
    table_name = "users"
    columns = ["user_id", "username"]
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    );
    '''


class Media(Database):
    table_name = "media"
    columns = ("user_id", "media_type", "file_id", "caption", "media_id", "description")

    @classmethod
    def create_table(cls) -> None:
        create_main_table_query = """
            CREATE TABLE IF NOT EXISTS media (
                user_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                file_id TEXT NOT NULL UNIQUE,
                caption TEXT,
                media_id INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """
        create_table_fts_query = """
        CREATE VIRTUAL TABLE IF NOT EXISTS media_fts USING fts5(
            media_id,
            description
        );
        """
        cls.execute_query(create_main_table_query)
        cls.execute_query(create_table_fts_query)

    @classmethod
    def add(cls, data: dict, replace: bool = False) -> tuple[bool, int]:
        media_data = {
            'user_id': data["user_id"],
            'media_type': data["media_type"],
            'file_id': data["file_id"],
            'caption': data.get("caption", None),
        }
        description = data["description"]

        [status, media_id] = super().add(media_data)
        if status:
            cls.execute_query('INSERT INTO media_fts (media_id, description) VALUES (?, ?);', (media_id, description))
        return status, media_id

    @classmethod
    def get(cls, conditions: dict = None, limit: int = None, offset: int = None,
            order_by: str = None, sort_direction: str = 'ASC', include_column_names=False, custom_select=None) -> list or dict or tuple:
        joined_select = """
        SELECT media.*, media_fts.description 
        FROM media 
        LEFT JOIN media_fts ON media.media_id = media_fts.media_id
        """
        custom_select = custom_select or joined_select
        return super().get(conditions, limit, offset, order_by, sort_direction, include_column_names, custom_select)

    @classmethod
    def delete(cls, conditions: dict):
        """Deletes records that meet the given conditions from both media and media_fts tables."""
        if not conditions:
            raise ValueError("No conditions provided for identifying the row(s) to delete.")

        if 'description' in conditions:
            raise NotImplementedError("Deletion by description is not supported.")

        cls.validate_columns(conditions)

        where_clause = ' AND '.join(f"{key} = ?" for key in conditions)

        delete_fts_query = f"""
            DELETE FROM media_fts
            WHERE media_id IN (
                SELECT media_id FROM media 
                WHERE {where_clause}
            );
        """
        delete_media_query = f"""
            DELETE FROM media
            WHERE {where_clause};
        """

        params = tuple(conditions.values())

        cls.execute_query(delete_fts_query, params)
        cursor_media = cls.execute_query(delete_media_query, params)

        return cursor_media.rowcount > 0

    @classmethod
    def search_by_description(cls, user_id: int, description: str, limit: int = None, offset: int = None) -> tuple[list, int]:
        """
        Searches media by description using Full-Text Search (FTS).

        :param user_id: The ID of the user whose media to search
        :param description: The text to search in the description
        :param limit: Maximum number of records to retrieve (optional)
        :param offset: Number of records to skip (optional)
        :return: A tuple containing the list of media entries and the total count of records
        """
        params = [user_id]

        if description:
            # Split the description into individual search terms and add prefix search
            search_terms = [f"{term}*" for term in description.split()]
            # Create a search string with terms combined by OR
            search_query = ' OR '.join(search_terms)

            # Query to select media matching the search description
            query = f"""
                SELECT media.*, media_fts.description 
                FROM media
                JOIN media_fts ON media.media_id = media_fts.media_id
                WHERE media_fts.description MATCH ? AND media.user_id = ?
                ORDER BY rank
            """
            params.insert(0, search_query)

            # Count query to get total matching records including media_fts
            count_query = f"""
                SELECT COUNT(*) 
                FROM media
                JOIN media_fts ON media.media_id = media_fts.media_id
                WHERE media_fts.description MATCH ? AND media.user_id = ?
            """
            total_count_params = [search_query, user_id]

        else:  # If description is empty, fetch all records for the user
            # Query to select all media for the specified user
            query = f"""
                SELECT media.*, media_fts.description 
                FROM media
                JOIN media_fts ON media.media_id = media_fts.media_id
                WHERE media.user_id = ?
                ORDER BY rank
            """

            # Count query for total records for the user
            count_query = """
                SELECT COUNT(*) 
                FROM media
                WHERE user_id = ?
            """
            total_count_params = [user_id]

        # Execute the count query to get total number of records
        total_count = cls.execute_query(count_query, total_count_params)[0][0]

        if limit:
            # Add LIMIT clause if a limit is specified
            query += " LIMIT ?"
            params.append(limit)

        if offset:
            if limit:
                # Add OFFSET clause if both limit and offset are specified
                query += " OFFSET ?"
                params.append(offset)
            else:
                # Raise an error if offset is specified without limit
                raise ValueError("Offset cannot be specified without a limit.")

        # Execute the main query to fetch media records
        records = cls.execute_query(query, params)

        # Return both the fetched records and the total count of records
        return records, total_count


class Temp(Database):
    table_name = "temp"
    columns = ("user_id", "key", "value")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS temp (
        user_id INTEGER,
        key TEXT,
        value TEXT,
        PRIMARY KEY (user_id, key),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """

    @classmethod
    def add(cls, data: dict, replace: bool = True) -> tuple[bool, int]:
        return super().add(data, replace=replace)
