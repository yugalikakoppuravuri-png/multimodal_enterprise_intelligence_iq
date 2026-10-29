"""
Tabular Data Loader (CSV & Excel)
Provides high-performance spreadsheet parsing, schema extraction,
column statistics, and in-memory SQLite table registration for exact SQL queries.
"""

import os
import csv
import io
import sqlite3
import re
from typing import Dict, List, Any, Tuple, Optional
import openpyxl


class TabularData:
    """Represents an ingested tabular dataset (CSV or Excel sheet)."""
    def __init__(self, name: str, headers: List[str], rows: List[List[Any]], sheet_name: Optional[str] = None):
        self.name = name
        self.sheet_name = sheet_name or "default"
        self.headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(headers)]
        # Clean header names for SQLite (alphanumeric and underscore only)
        self.clean_headers = [re.sub(r'[^a-zA-Z0-9_]', '_', h.lower()) for h in self.headers]
        # Ensure unique clean headers
        seen = {}
        for i, h in enumerate(self.clean_headers):
            if not h or h[0].isdigit():
                h = f"col_{h}"
            if h in seen:
                seen[h] += 1
                self.clean_headers[i] = f"{h}_{seen[h]}"
            else:
                seen[h] = 0
                self.clean_headers[i] = h

        self.rows = rows
        self.num_rows = len(rows)
        self.num_cols = len(self.headers)
        self.stats = self._compute_statistics()

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute basic summary statistics for numeric and categorical columns."""
        col_data: Dict[str, List[Any]] = {h: [] for h in self.headers}
        for row in self.rows:
            for i, val in enumerate(row):
                if i < len(self.headers):
                    col_data[self.headers[i]].append(val)

        stats = {}
        for header, vals in col_data.items():
            # Check if numeric
            num_vals = []
            for v in vals:
                if v is None or v == "":
                    continue
                try:
                    # Clean currency or commas e.g. "$1,200.50" -> 1200.50
                    if isinstance(v, str):
                        v_clean = re.sub(r'[\$,]', '', v.strip())
                        num_vals.append(float(v_clean))
                    elif isinstance(v, (int, float)):
                        num_vals.append(float(v))
                except (ValueError, TypeError):
                    pass

            if len(num_vals) > 0 and len(num_vals) >= len(vals) * 0.5:
                # Treat as numeric
                stats[header] = {
                    "type": "numeric",
                    "count": len(num_vals),
                    "min": min(num_vals),
                    "max": max(num_vals),
                    "sum": round(sum(num_vals), 2),
                    "mean": round(sum(num_vals) / len(num_vals), 2)
                }
            else:
                # Treat as categorical/text
                str_vals = [str(v) for v in vals if v is not None and v != ""]
                unique_vals = list(set(str_vals))
                stats[header] = {
                    "type": "text",
                    "count": len(str_vals),
                    "unique_count": len(unique_vals),
                    "sample_values": unique_vals[:5]
                }
        return stats

    def to_markdown(self, max_rows: int = 10) -> str:
        """Render markdown representation of the table."""
        lines = []
        lines.append("| " + " | ".join(self.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")
        for row in self.rows[:max_rows]:
            row_str = [str(val) if val is not None else "" for val in row]
            # Pad if row is shorter than headers
            while len(row_str) < len(self.headers):
                row_str.append("")
            lines.append("| " + " | ".join(row_str[:len(self.headers)]) + " |")
        if self.num_rows > max_rows:
            lines.append(f"\n*(Showing {max_rows} of {self.num_rows} total rows)*")
        return "\n".join(lines)

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Convert rows to list of dictionaries."""
        records = []
        for row in self.rows:
            d = {}
            for i, h in enumerate(self.headers):
                d[h] = row[i] if i < len(row) else None
            records.append(d)
        return records


class TabularEngine:
    """Manages tabular data parsing and in-memory SQLite querying."""
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.tables: Dict[str, TabularData] = {}

    def load_file(self, file_path_or_bytes: Any, filename: str) -> List[TabularData]:
        """Load CSV or Excel file and register into SQLite."""
        tables = []
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".csv":
            tables.append(self._load_csv(file_path_or_bytes, filename))
        elif ext in [".xlsx", ".xls"]:
            tables.extend(self._load_excel(file_path_or_bytes, filename))
        else:
            raise ValueError(f"Unsupported tabular file format: {ext}")

        for t in tables:
            table_key = f"{t.name}_{t.sheet_name}".replace(" ", "_").replace("-", "_")
            self.tables[table_key] = t
            self._register_sqlite(table_key, t)

        return tables

    def _load_csv(self, file_input: Any, filename: str) -> TabularData:
        """Parse CSV file."""
        if isinstance(file_input, (str, os.PathLike)) and os.path.exists(str(file_input)):
            with open(file_input, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        elif isinstance(file_input, str):
            content = file_input
        elif hasattr(file_input, "read"):
            raw = file_input.read()
            if isinstance(raw, bytes):
                content = raw.decode("utf-8", errors="replace")
            else:
                content = str(raw)
        elif isinstance(file_input, bytes):
            content = file_input.decode("utf-8", errors="replace")
        else:
            content = str(file_input)

        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        if not rows:
            return TabularData(filename, [], [])
        headers = rows[0]
        data_rows = rows[1:]
        return TabularData(filename, headers, data_rows, sheet_name="data")

    def _load_excel(self, file_input: Any, filename: str) -> List[TabularData]:
        """Parse Excel workbook with openpyxl."""
        if isinstance(file_input, (str, os.PathLike)):
            wb = openpyxl.load_workbook(file_input, data_only=True)
        elif hasattr(file_input, "read"):
            data = file_input.read()
            wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        elif isinstance(file_input, bytes):
            wb = openpyxl.load_workbook(io.BytesIO(file_input), data_only=True)
        else:
            raise ValueError("Invalid Excel input")

        tables = []
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            rows = list(ws.iter_rows(values_only=True))
            if not rows or len(rows) < 1:
                continue
            # find first row with content as header
            header_idx = 0
            while header_idx < len(rows) and not any(rows[header_idx]):
                header_idx += 1
            if header_idx >= len(rows):
                continue

            headers = [str(c) if c is not None else f"col_{i}" for i, c in enumerate(rows[header_idx])]
            data_rows = [list(r) for r in rows[header_idx + 1:] if any(r)]
            t = TabularData(name=filename, headers=headers, rows=data_rows, sheet_name=sheet)
            tables.append(t)
        return tables

    def _register_sqlite(self, table_name: str, table_data: TabularData):
        """Create and populate an in-memory SQLite table."""
        # Sanitize table name
        safe_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        if safe_table_name[0].isdigit():
            safe_table_name = f"t_{safe_table_name}"

        cursor = self.conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {safe_table_name}")

        col_defs = []
        for clean_h, orig_h in zip(table_data.clean_headers, table_data.headers):
            stat = table_data.stats.get(orig_h, {})
            if stat.get("type") == "numeric":
                col_defs.append(f'"{clean_h}" REAL')
            else:
                col_defs.append(f'"{clean_h}" TEXT')

        create_sql = f'CREATE TABLE {safe_table_name} ({", ".join(col_defs)})'
        cursor.execute(create_sql)

        # Insert rows
        placeholders = ", ".join(["?"] * len(table_data.clean_headers))
        insert_sql = f'INSERT INTO {safe_table_name} VALUES ({placeholders})'

        cleaned_rows = []
        for row in table_data.rows:
            clean_row = []
            for i, clean_h in enumerate(table_data.clean_headers):
                orig_h = table_data.headers[i] if i < len(table_data.headers) else ""
                val = row[i] if i < len(row) else None
                stat = table_data.stats.get(orig_h, {})
                if stat.get("type") == "numeric" and val is not None:
                    try:
                        clean_val = float(re.sub(r'[\$,]', '', str(val).strip()))
                        clean_row.append(clean_val)
                    except (ValueError, TypeError):
                        clean_row.append(None)
                else:
                    clean_row.append(str(val) if val is not None else None)
            cleaned_rows.append(clean_row)

        cursor.executemany(insert_sql, cleaned_rows)
        self.conn.commit()

    def query(self, sql_query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Execute read-only SQL query against registered tables."""
        cursor = self.conn.cursor()
        cursor.execute(sql_query)
        headers = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return headers, rows

    def generate_summary_text(self, table: TabularData) -> str:
        """Generate comprehensive natural language summary of table for RAG indexing."""
        parts = [
            f"Dataset: '{table.name}', Sheet: '{table.sheet_name}'",
            f"Dimensions: {table.num_rows} rows x {table.num_cols} columns",
            f"Columns: {', '.join(table.headers)}",
            "\nColumn Metrics & Statistics:"
        ]
        for col, stat in table.stats.items():
            if stat["type"] == "numeric":
                parts.append(
                    f"- {col} (Numeric): Sum={stat['sum']:,}, Mean={stat['mean']:,}, "
                    f"Min={stat['min']:,}, Max={stat['max']:,} (from {stat['count']} values)"
                )
            else:
                samples = ", ".join([f"'{s}'" for s in stat["sample_values"]])
                parts.append(
                    f"- {col} (Text): {stat['unique_count']} unique values. Samples: [{samples}]"
                )

        parts.append("\nSample Data Preview:")
        parts.append(table.to_markdown(max_rows=5))
        return "\n".join(parts)
