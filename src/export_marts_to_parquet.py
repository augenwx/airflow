import os
import duckdb
from pathlib import Path

def main():
    project_root = Path(os.getenv("PROJECT_ROOT", "/mnt/d/mineria data/airflow"))
    db_path = project_root / "data" / "warehouse" / "predictit.duckdb"
    export_dir = project_root / "data" / "tableau_export"
    
    # Ensure export directory exists
    export_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Connecting to DuckDB at {db_path}...")
    con = duckdb.connect(str(db_path), read_only=True)
    
    # Get all tables in main_marts schema
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='main_marts'"
    tables = con.execute(query).fetchall()
    
    print(f"Found {len(tables)} tables in main_marts. Exporting to Parquet...")
    
    for t in tables:
        table_name = t[0]
        out_file = export_dir / f"{table_name}.parquet"
        
        # Copy table to parquet file
        print(f"Exporting {table_name} -> {out_file.name}")
        con.execute(f"COPY main_marts.{table_name} TO '{str(out_file)}' (FORMAT PARQUET)")
        
    print("Export complete. These files are ready for Tableau!")

if __name__ == "__main__":
    main()
