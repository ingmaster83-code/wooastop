# -*- coding: utf-8 -*-
"""전국휴게소정보표준데이터 API -> _rawdata/reststops_raw.json"""
import json
import urllib.request
import urllib.parse
from pathlib import Path

API_KEY = "9490b1d34e92aa9e25b32a4cff1438fc7b9c71e5d332413916a391e867f61e86"
BASE_URL = "https://api.data.go.kr/openapi/tn_pubr_public_rest_area_api"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_rawdata" / "reststops_raw.json"


def fetch_page(page_no, num_of_rows=100):
    params = {
        "serviceKey": API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "type": "json",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["response"]["body"]


def main():
    all_items = []
    page = 1
    while True:
        body = fetch_page(page)
        items = body.get("items", [])
        if not items:
            break
        all_items.extend(items)
        total = int(body.get("totalCount", 0))
        print(f"page {page}: +{len(items)} (누적 {len(all_items)} / 총 {total})")
        if len(all_items) >= total:
            break
        page += 1

    OUT.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"완료: {len(all_items)}건 -> {OUT}")


if __name__ == "__main__":
    main()
