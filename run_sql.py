"""Run .sql scripts against a SQLite database file and print every SELECT result.

Arguments: [--fresh] DATABASE_FILE SCRIPT.sql [SCRIPT.sql ...]
--fresh deletes the database file first so the build starts from nothing.
Uses only Python's standard library, so it works offline on Windows, macOS and Linux.
"""
import os
import sqlite3
import sys


def split_statements(sql_text):
    """Split a script into single statements.

    sqlite3.complete_statement knows about quotes, comments and BEGIN...END
    trigger bodies, so a ';' inside any of those does not end the statement.
    It is asked after every ';', so two statements on one line are split too.
    """
    statements = []
    buffer = ""
    for line in sql_text.splitlines():
        pieces = line.split(";")
        for number, piece in enumerate(pieces):
            buffer += piece + (";" if number < len(pieces) - 1 else "\n")
            if sqlite3.complete_statement(buffer):
                if strip_comments(buffer):
                    statements.append(buffer.strip())
                buffer = ""
    if strip_comments(buffer):
        raise ValueError("Script ends with an unfinished statement (missing ';'?):\n" + buffer.strip())
    return statements


def strip_comments(text):
    """Return the text without '--' comment lines, used to skip comment-only chunks."""
    kept = [line for line in text.splitlines() if not line.strip().startswith("--")]
    return "\n".join(kept).strip().strip(";").strip()


def read_script(path):
    # utf-8-sig drops a byte-order mark if an editor added one; splitlines() handles CRLF.
    with open(path, encoding="utf-8-sig") as handle:
        return handle.read()


def connect(db_path):
    # isolation_level=None: the scripts' own BEGIN/COMMIT control transactions, as in DBeaver.
    connection = sqlite3.connect(db_path, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def run_script(connection, sql_text, out=None):
    """Execute every statement and return [(column_names, rows), ...] for each one
    that produced a result set. With out set, also print each result as a table."""
    results = []
    for statement in split_statements(sql_text):
        try:
            cursor = connection.execute(statement)
        except sqlite3.Error:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        if cursor.description is not None:
            rows = cursor.fetchall()
            results.append(([column[0] for column in cursor.description], rows))
            if out is not None:
                print_table(cursor.description, rows, out)
    return results


def format_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def print_table(description, rows, out):
    headers = [column[0] for column in description]
    cells = [[format_value(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in cells:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    out.write(" | ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip() + "\n")
    out.write("-+-".join("-" * w for w in widths) + "\n")
    for row in cells:
        out.write(" | ".join(c.ljust(w) for c, w in zip(row, widths)).rstrip() + "\n")
    out.write(f"({len(rows)} row{'' if len(rows) == 1 else 's'})\n\n")


def main(argv):
    args = list(argv)
    fresh = "--fresh" in args
    if fresh:
        args.remove("--fresh")
    if len(args) < 2:
        script_name = os.path.basename(sys.argv[0])
        print(f"usage: python {script_name} [--fresh] wildlife.db sql/06_reports.sql")
        print(__doc__.strip())
        return 2
    db_path, scripts = args[0], args[1:]
    if fresh and os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError as error:
            # Windows refuses to delete a file another program (DBeaver) has open.
            print(f"ERROR: cannot delete {db_path} ({error.strerror}). Disconnect it in DBeaver first.")
            return 1
    connection = connect(db_path)
    try:
        for script in scripts:
            run_script(connection, read_script(script), sys.stdout)
            print(f"OK: {script}")
    except (sqlite3.Error, ValueError, OSError) as error:
        print(f"ERROR in {script}: {error}")
        return 1
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))