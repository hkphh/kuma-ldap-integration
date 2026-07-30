#!/usr/bin/env python3

import sys
import subprocess
import requests
from pathlib import Path

requests.packages.urllib3.disable_warnings()

HOST = "kuma.example.ru:7223"
TOKEN = "<TOKEN>"
DICT_ID = "<DICT>

def post_kuma(files: dict) -> str:
    result = requests.post(
        f"https://{HOST}/api/v3/dictionaries/update",
        params={"dictionaryID": DICT_ID, "needReload": 0},
        headers={"Authorization": f"Bearer {TOKEN}"},
        files=files,
        verify=False
        )
    return result

def uniq(text: str) -> str:

    lines = text.strip().splitlines()
    seen = set()
    result = []
    result.append("key,value")
    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line + ",")
    return "\n".join(result)       

def parse(data: str, filename: str = "content.csv") -> dict:
    data = uniq(data)
    data_bytes = data.encode("utf-8")
    return {"file": (filename, data_bytes, "text/csv")}

def get_query(connection: subprocess.Popen) -> str:
    sql = """
SELECT sam_account_name || '|' || domain
FROM accounts
WHERE archived = 0
AND (member_of LIKE '%SuperAdminGroup%'
OR member_of LIKE '%Remote Assistants%');
"""
    stdout, _ = connection.communicate(input=sql)
    return stdout


def init_sql() -> subprocess.Popen:
    proc = subprocess.Popen(
    ["/opt/kaspersky/kuma/kuma", "tools", "sql",
     "--cert", "/opt/kaspersky/kuma/core/00000000-0000-0000-0000-000000000000/certificates/internal.cert",
     "--key", "/opt/kaspersky/kuma/core/00000000-0000-0000-0000-000000000000/certificates/internal.key"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return proc


def main() -> str:
    conn = init_sql()
    raw_data = get_query(conn)
    parsed_data = parse(raw_data)
    result = post_kuma(parsed_data)
    print("Result is code:", result.status_code, "\nAnswer:" ,result.json())

if __name__ == "__main__":
    
    if len(sys.argv) != 1:
        print("Usage: python <scriptname>")
        exit()

    main()
