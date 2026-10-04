"""
HYDRA-SQL Python Client & SDK
High-Performance Zero-Copy Binary Database Engine Wrapper (SQL Interface)
"""

import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

OPENER_BIN = os.path.join(BIN_DIR, "otworz_baze")
CREATOR_BIN = os.path.join(BIN_DIR, "stworz_baze")
CLI_BIN = os.path.join(BIN_DIR, "hydra_db_cli")

class HydraDatabase:
    """Python wrapper for HYDRA-SQL Zero-Copy Binary Database Engine with SQL DDL/DML Support."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def execute_sql(self, sql_statement: str):
        """Executes a SQL statement (CREATE TABLE, INSERT INTO) on the binary database."""
        cmd = [CREATOR_BIN, "sql", self.db_path, sql_statement]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"SQL Execution Error: {res.stderr}")
        return res.stdout.strip()

    @staticmethod
    def create_llm_dataset(output_path: str, num_records: int = 100000):
        """Generates a binary LLM dataset file with specified record count."""
        cmd = [CREATOR_BIN, "llm", output_path, str(num_records)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to create LLM dataset: {res.stderr}")
        return res.stdout.strip()

    def inspect(self, query_id_or_filter: str = None):
        """Queries the binary database with O(1) direct offset indexing."""
        cmd = [OPENER_BIN, self.db_path]
        if query_id_or_filter is not None:
            cmd.append(str(query_id_or_filter))
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.stdout.strip()

if __name__ == "__main__":
    print("=== HYDRA-SQL Python SDK (SQL Interface Demo) ===")
    db_file = "company_employees.bin"

    db = HydraDatabase(db_file)
    
    print("\n[1] Executing SQL CREATE TABLE...")
    print(db.execute_sql("CREATE TABLE pracownicy (id INT, imie TEXT, nazwisko TEXT, stanowisko TEXT, dzial TEXT, pensja INT)"))

    print("\n[2] Executing SQL INSERT Statements...")
    print(db.execute_sql("INSERT INTO pracownicy VALUES (1, 'Jan', 'Kowalski', 'DevOps Architect', 'IT Ops', 18500)"))
    print(db.execute_sql("INSERT INTO pracownicy VALUES (2, 'Anna', 'Nowak', 'AI Engineer', 'R&D', 22000)"))

    print("\n[3] Reading Database Contents (Zero-Copy O(1) Read):")
    print(db.inspect())
