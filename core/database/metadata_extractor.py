import asyncio
import pymysql
import pandas as pd
from typing import Dict, Any, Optional
from settings_config import Settings

class DatabaseMetadataExtractor:
    """
    A class to extract and analyze metadata from MySQL database schemas,
    optimized for large insurance databases with 300+ tables.
    """
    settings = Settings()
    def __init__(self):
        """Initialize the extractor with database connection parameters."""
        self.connection_params = {
            "host": self.settings.database.host,
            "port": self.settings.database.port,
            "user": self.settings.database.user,
            "password": self.settings.database.password,
            "database": self.settings.database.database,
            "charset": self.settings.database.charset,
            "cursorclass": pymysql.cursors.DictCursor
        }
        
    def _get_connection(self):
        """Create and return a database connection."""
        return pymysql.connect(**self.connection_params)
    
    def extract_tables(self) -> pd.DataFrame:
        """Extract all tables in the database."""
        query = """
        SELECT 
            TABLE_NAME as table_name, 
            TABLE_COMMENT as description,
            TABLE_ROWS as row_count,
            CREATE_TIME as created_at,
            UPDATE_TIME as updated_at
        FROM 
            INFORMATION_SCHEMA.TABLES 
        WHERE 
            TABLE_SCHEMA = %s
        ORDER BY 
            TABLE_NAME
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (self.connection_params["database"],))
                tables = cursor.fetchall()
                
        return pd.DataFrame(tables)
    
    def extract_columns(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """Extract column details for a specific table or all tables."""
        query = """
        SELECT 
            TABLE_NAME as table_name,
            COLUMN_NAME as column_name,
            COLUMN_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            COLUMN_KEY as key_type,
            COLUMN_COMMENT as description,
            EXTRA as extra
        FROM 
            INFORMATION_SCHEMA.COLUMNS 
        WHERE 
            TABLE_SCHEMA = %s
        """
        
        params = [self.connection_params["database"]]
        
        if table_name:
            query += " AND TABLE_NAME = %s"
            params.append(table_name)
            
        query += " ORDER BY TABLE_NAME, ORDINAL_POSITION"
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                columns = cursor.fetchall()
                
        return pd.DataFrame(columns)
    
    def extract_foreign_keys(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """Extract foreign key relationships for a specific table or all tables."""
        query = """
        SELECT 
            k.TABLE_NAME as table_name,
            k.COLUMN_NAME as column_name,
            k.REFERENCED_TABLE_NAME as referenced_table,
            k.REFERENCED_COLUMN_NAME as referenced_column,
            c.UPDATE_RULE as update_rule,
            c.DELETE_RULE as delete_rule
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
        JOIN 
            INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS c
        ON 
            k.CONSTRAINT_NAME = c.CONSTRAINT_NAME AND
            k.CONSTRAINT_SCHEMA = c.CONSTRAINT_SCHEMA
        WHERE 
            k.TABLE_SCHEMA = %s AND
            k.REFERENCED_TABLE_SCHEMA = %s
        """
        
        params = [self.connection_params["database"], self.connection_params["database"]]
        
        if table_name:
            query += " AND (k.TABLE_NAME = %s OR k.REFERENCED_TABLE_NAME = %s)"
            params.extend([table_name, table_name])
            
        query += " ORDER BY k.TABLE_NAME, k.COLUMN_NAME"
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                foreign_keys = cursor.fetchall()
                
        return pd.DataFrame(foreign_keys)
    
    def find_tables_by_keyword(self, keyword: str) -> pd.DataFrame:
        """Find tables that might be related to a specific keyword, including foreign key relationships."""
        query = """
        WITH related_tables AS (
            -- Direct table matches
            SELECT 
                t.TABLE_NAME as table_name, 
                t.TABLE_COMMENT as description,
                'direct_match' as relationship_type
            FROM 
                INFORMATION_SCHEMA.TABLES t
            WHERE 
                t.TABLE_SCHEMA = %s AND
                (
                    t.TABLE_NAME LIKE %s OR
                    t.TABLE_COMMENT LIKE %s
                )
            
            UNION
            
            -- Column matches
            SELECT 
                c.TABLE_NAME as table_name,
                t.TABLE_COMMENT as description,
                'column_match' as relationship_type
            FROM 
                INFORMATION_SCHEMA.COLUMNS c
            JOIN
                INFORMATION_SCHEMA.TABLES t
            ON
                c.TABLE_NAME = t.TABLE_NAME AND
                c.TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE 
                c.TABLE_SCHEMA = %s AND
                (
                    c.COLUMN_NAME LIKE %s OR
                    c.COLUMN_COMMENT LIKE %s
                )
            
            UNION
            
            -- Foreign key relationships (tables that reference the matched tables)
            SELECT DISTINCT
                k.TABLE_NAME as table_name,
                t.TABLE_COMMENT as description,
                'referenced_by' as relationship_type
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
            JOIN 
                INFORMATION_SCHEMA.TABLES t
            ON 
                k.TABLE_NAME = t.TABLE_NAME AND
                k.TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE 
                k.TABLE_SCHEMA = %s AND
                k.REFERENCED_TABLE_NAME IN (
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s AND
                    (
                        TABLE_NAME LIKE %s OR
                        TABLE_COMMENT LIKE %s
                    )
                )
            
            UNION
            
            -- Tables that are referenced by the matched tables
            SELECT DISTINCT
                k.REFERENCED_TABLE_NAME as table_name,
                t.TABLE_COMMENT as description,
                'references' as relationship_type
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
            JOIN 
                INFORMATION_SCHEMA.TABLES t
            ON 
                k.REFERENCED_TABLE_NAME = t.TABLE_NAME AND
                k.REFERENCED_TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE 
                k.TABLE_SCHEMA = %s AND
                k.TABLE_NAME IN (
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s AND
                    (
                        TABLE_NAME LIKE %s OR
                        TABLE_COMMENT LIKE %s
                    )
                )
        )
        SELECT 
            table_name,
            description,
            GROUP_CONCAT(DISTINCT relationship_type) as relationships
        FROM 
            related_tables
        GROUP BY 
            table_name, description
        ORDER BY 
            table_name
        """
        
        search_pattern = f"%{keyword}%"
        params = [
            self.connection_params["database"], search_pattern, search_pattern,  # Direct matches
            self.connection_params["database"], search_pattern, search_pattern,  # Column matches
            self.connection_params["database"], self.connection_params["database"], search_pattern, search_pattern,  # Referenced by
            self.connection_params["database"], self.connection_params["database"], search_pattern, search_pattern   # References
        ]
        
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                tables = cursor.fetchall()
                
        return pd.DataFrame(tables)
    
    # NOTE: This function has not been implemented yet
    def analyze_feature_related_schema(self, feature_keyword: str) -> Dict[str, Any]:
        """
        Analyze and return tables and relationships related to a specific feature.
        For example, to understand the "member upload feature", we would look for
        tables related to members, uploads, etc.
        """
        # Implementation details...
        pass
