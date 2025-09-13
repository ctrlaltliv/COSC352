#!/usr/bin/env python3
"""
read_html_tables_save_html.py
-----------------------------
Reads all HTML tables from a URL or local file and outputs each table as a separate CSV.
Also saves the raw HTML of the URL to a local file.

Usage:
    python read_html_tables_save_html.py <URL|FILENAME>

Notes:
- Works with pages that contain <table> HTML elements.
- Only uses standard Python libraries.
- Saves CSV files as output_1.csv, output_2.csv, etc.
- Saves HTML file as page.html if the input is a URL.
"""

import sys
import urllib.request
import os

def fetch_html(source):
    """Fetch HTML from a URL or local file with User-Agent to bypass 403."""
    if source.startswith("http://") or source.startswith("https://"):
        req = urllib.request.Request(
            source,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Save the HTML locally
            with open("page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("HTML saved as page.html")
            return html
    elif os.path.exists(source):
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print("Error: source not found.")
        sys.exit(1)

def extract_tables(html):
    """Extract all <table> ... </table> blocks from HTML."""
    tables = []
    pos = 0
    while True:
        start = html.find("<table", pos)
        if start == -1:
            break
        end = html.find("</table>", start)
        if end == -1:
            break
        table_html = html[start:end+8]
        tables.append(table_html)
        pos = end + 8
    return tables

def parse_table(table_html):
    """Parse table HTML and return list of rows, each as a list of cells."""
    rows = []
    pos = 0
    while True:
        row_start = table_html.find("<tr", pos)
        if row_start == -1:
            break
        row_end = table_html.find("</tr>", row_start)
        if row_end == -1:
            break
        row_html = table_html[row_start:row_end]
        cells = []
        cell_pos = 0
        while True:
            td_start = row_html.find("<td", cell_pos)
            th_start = row_html.find("<th", cell_pos)
            if td_start == -1 and th_start == -1:
                break
            if td_start != -1 and (td_start < th_start or th_start == -1):
                cell_start = row_html.find(">", td_start) + 1
                cell_end = row_html.find("</td>", cell_start)
                cell = row_html[cell_start:cell_end].strip()
                cells.append(clean_html(cell))
                cell_pos = cell_end + 5
            else:
                cell_start = row_html.find(">", th_start) + 1
                cell_end = row_html.find("</th>", cell_start)
                cell = row_html[cell_start:cell_end].strip()
                cells.append(clean_html(cell))
                cell_pos = cell_end + 5
        rows.append(cells)
        pos = row_end + 5
    return rows

def clean_html(text):
    """Remove simple HTML tags and newlines from cell text."""
    while "<" in text and ">" in text:
        lt = text.find("<")
        gt = text.find(">", lt)
        if lt == -1 or gt == -1:
            break
        text = text[:lt] + text[gt+1:]
    return text.replace("\n", " ").replace("\r", " ").strip()

def save_csv(rows, filename):
    """Save the table as CSV."""
    with open(filename, "w", encoding="utf-8") as f:
        for row in rows:
            line = ",".join(['"{}"'.format(cell.replace('"', '""')) for cell in row])
            f.write(line + "\n")
    print(f"CSV saved as {filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python read_html_tables_save_html.py <URL|FILENAME>")
        sys.exit(1)

    source = sys.argv[1]
    html = fetch_html(source)
    tables = extract_tables(html)

    if not tables:
        print("No tables found in the HTML.")
        sys.exit(1)

    for i, table_html in enumerate(tables, start=1):
        rows = parse_table(table_html)
        if rows:  # Only save non-empty tables
            filename = f"output_{i}.csv"
            save_csv(rows, filename)

if __name__ == "__main__":
    main()
