# -*- coding: utf-8 -*-
"""_rawdata/reststops_raw.json -> _data/reststops.json 변환"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_rawdata" / "reststops_raw.json"
OUT = ROOT / "_data" / "reststops.json"

ROUTE_SLUG = {
    "경부선": "gyeongbu",
    "서해안선": "seohaean",
    "호남선": "honam",
    "영동선": "yeongdong",
    "중앙선": "jungang",
    "중부내륙선": "jungbu-naeryuk",
    "중부내륙": "jungbu-naeryuk",
    "남해선": "namhae",
    "대전통영선": "daejeon-tongyeong",
    "광주대구선": "gwangju-daegu",
    "당진영덕선": "dangjin-yeongdeok",
    "중부선": "jungbu",
    "평택제천선": "pyeongtaek-jecheon",
    "순천완주선": "suncheon-wanju",
    "동해선": "donghae",
    "중부내륙지선": "jungbu-naeryukji",
    "대구포항선": "daegu-pohang",
    "상주영덕선": "sangju-yeongdeok",
    "서울양양선": "seoul-yangyang",
    "수도권제1순환선": "sudogwon-1",
    "호남지선": "honamji",
    "서천공주선": "seocheon-gongju",
    "함양울산선": "hamyang-ulsan",
    "울산포항선": "ulsan-pohang",
    "밀양울산선": "miryang-ulsan",
    "익산장수선": "iksan-jangsu",
    "무안광주선": "muan-gwangju",
    "부산외곽선": "busan-oegwak",
    "세종포천선": "sejong-pocheon",
    "남해제2지선": "namhae-2ji",
}

TYPE_MAP = {
    "일반휴게소": {"slug": "general", "label": "일반휴게소", "icon": "🍽️"},
    "간이휴게소": {"slug": "simple", "label": "간이휴게소", "icon": "🚻"},
    "화물차휴게소": {"slug": "truck", "label": "화물차휴게소", "icon": "🚛"},
}

FACILITY_LABELS = {
    "oltYn": "⛽ 주유소",
    "lpgYn": "🔥 LPG충전",
    "elctyYn": "🔌 전기차충전",
    "busTrnsitYn": "🚌 버스환승",
    "shltrYn": "☂️ 쉼터",
    "toiletYn": "🚻 화장실",
    "parmacyYn": "💊 약국",
    "nrsgYn": "🍼 수유실",
    "shopYn": "🛒 편의점",
    "rstrtYn": "🍚 식당",
    "crrpwrkYn": "🔧 정비소",
}


def fmt_time(hhmm):
    hhmm = (hhmm or "").strip()
    if not hhmm:
        return ""
    if ":" in hhmm:
        return hhmm
    if len(hhmm) == 4 and hhmm.isdigit():
        return f"{hhmm[:2]}:{hhmm[2:]}"
    return hhmm


def main():
    raw = json.loads(SRC.read_text(encoding="utf-8"))

    route_seq = {}
    stops = []
    skipped = 0

    for r in raw:
        name = (r.get("entrpsNm") or "").strip()
        route_nm = (r.get("roadRouteNm") or "").strip()
        route_slug = ROUTE_SLUG.get(route_nm)
        if not name or not route_slug:
            skipped += 1
            continue

        route_seq[route_slug] = route_seq.get(route_slug, 0) + 1
        slug = f"{route_slug}-{route_seq[route_slug]:03d}"

        raw_type = (r.get("restAreaType") or "일반휴게소").strip()
        type_info = TYPE_MAP.get(raw_type, TYPE_MAP["일반휴게소"])

        facilities = [label for key, label in FACILITY_LABELS.items() if r.get(key) == "Y"]

        etc = (r.get("etcCvntl") or "").strip()

        stops.append({
            "slug": slug,
            "stopName": name,
            "routeSlug": route_slug,
            "routeName": route_nm,
            "routeNo": r.get("roadRouteNo", ""),
            "direction": r.get("roadRouteDrc", ""),
            "lat": r.get("latitude", ""),
            "lng": r.get("longitude", ""),
            "typeSlug": type_info["slug"],
            "typeLabel": type_info["label"],
            "typeIcon": type_info["icon"],
            "openTime": fmt_time(r.get("operOpenHhmm", "")),
            "closeTime": fmt_time(r.get("operCloseHhmm", "")),
            "area": r.get("ocpatAr", ""),
            "parking": r.get("prkplceCo", ""),
            "facilities": facilities,
            "etc": etc,
            "food": (r.get("rprsntvRstrt") or "").strip(),
            "phone": (r.get("phoneNumber") or "").strip(),
            "manageOrg": (r.get("insttNm") or "").strip(),
            "updated": r.get("referenceDate", ""),
        })

    OUT.write_text(json.dumps(stops, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"총 {len(raw)}건 중 {len(stops)}개 휴게소 저장, {skipped}개 스킵 -> {OUT}")

    route_count = {}
    for s in stops:
        route_count[s["routeName"]] = route_count.get(s["routeName"], 0) + 1
    print("노선별:", route_count)


if __name__ == "__main__":
    main()
