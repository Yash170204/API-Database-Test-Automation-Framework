import sqlite3
from typing import Any, Dict, List, Optional
from src.utils.logger import logger

class DBClient:
    """SQL-based Database Client wrapping sqlite3 to execute queries and assert consistency."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Helper to get connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as list of dictionaries."""
        params = params or ()
        logger.info(f"DB QUERY: {query} | Params: {params}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute_scalar(self, query: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Executes a query and returns the first column of the first row (e.g. COUNT(*))."""
        params = params or ()
        logger.info(f"DB SCALAR QUERY: {query} | Params: {params}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        finally:
            conn.close()

    def execute_fetchone(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Executes a query and returns a single row dictionary, or None."""
        params = params or ()
        logger.info(f"DB FETCHONE QUERY: {query} | Params: {params}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def execute_write(self, query: str, params: Optional[tuple] = None) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and commits. Returns affected row count."""
        params = params or ()
        logger.info(f"DB WRITE QUERY: {query} | Params: {params}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def clear_tables(self):
        """Clears all data from database tables."""
        logger.info("Clearing all records from database tables.")
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders;")
            cursor.execute("DELETE FROM products;")
            # Reset sqlite_sequence for autoincrement ids
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'orders');")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
