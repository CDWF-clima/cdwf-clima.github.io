import re
import urllib.request
import xml.etree.ElementTree as ET

# ── Webinar season playlists ───────────────────────────────────────────────────
SEASON_PLAYLISTS = {
    "2022": "PLSGSXuijkB6nllG5-O4U1Ut2dslgjiG5Q",
    "2023": "PLSGSXuijkB6l7xcbZfFBJLVnkkrQ8FiRi",
    "2024": "PLSGSXuijkB6mldY54HJy109_CJZ19WYiN",
    "2025": "PLSGSXuijkB6lVfGionx2m8e5h2czsX0oM",
    "2026": "PLSGSXuijkB6lLMe8sZ3fDkReWrH_5HdWC",
}

WEBINAR_HARDCODED = {
    "2022": [
        {"id": "y2FTkbNrVsw", "title": "Introductory Session"},
        {"id": "UN4AOWvf-cg", "title": "Clouds as we measure and understand"},
    ]
}

# ── Workshop playlists ─────────────────────────────────────────────────────────
WORKSHOP_PLAYLISTS = {
    "ML for Weather and Climate Prediction":        "PLSGSXuijkB6l2gIzgafo0DmKDyZYdIS_L",
    "Career in Climate Science":                    "PLBdpDWAkenAQ",
    "Science Communication":                        "PLSGSXuijkB6kcmKiMYusNlMLn201JhjBX",
}

ns = {
    "atom":  "http://www.w3.org/2005/Atom",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/"
}

def fetch_entries(playlist_id):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        root = ET.fromstring(r.read())
    results = []
    for e in root.findall("atom:entry", ns):
        vid       = e.find("yt:videoId", ns).text
        title     = e.find("atom:title", ns).text
        published = e.find("atom:published", ns).text
        mg        = e.find("media:group", ns)
        desc      = mg.find("media:description", ns).text or "" if mg is not None else ""
        results.append({"id": vid, "title": title, "published": published, "desc": desc})
    return results

# ══════════════════════════════════════════════════════════════════════════════
# 1. HOMEPAGE — Latest Webinar
# ══════════════════════════════════════════════════════════════════════════════
latest_webinar = fetch_entries(SEASON_PLAYLISTS["2026"])[0]
vid_id    = latest_webinar["id"]
vid_title = latest_webinar["title"]
vid_year  = latest_webinar["published"][:4]
lines     = [l for l in latest_webinar["desc"].split("\n") if l.strip()]
vid_desc  = "<br/>".join(lines[:5])

with open("index_template.html", "r", encoding="utf-8") as f:
    html = f.read()
html = re.sub(r"<!--WEBINAR_VIDEO_ID-->", vid_id,    html)
html = re.sub(r"<!--WEBINAR_TITLE-->",    vid_title, html)
html = re.sub(r"<!--WEBINAR_YEAR-->",     vid_year,  html)
html = re.sub(r"<!--WEBINAR_DESC-->",     vid_desc,  html)

# ══════════════════════════════════════════════════════════════════════════════
# 2. HOMEPAGE — Latest Workshop (newest across all 3 playlists)
# ══════════════════════════════════════════════════════════════════════════════
all_workshop_videos = []
for name, pid in WORKSHOP_PLAYLISTS.items():
    for v in fetch_entries(pid):
        v["playlist_name"] = name
        all_workshop_videos.append(v)

# Sort by published date, pick newest
all_workshop_videos.sort(key=lambda v: v["published"], reverse=True)
latest_ws = all_workshop_videos[0]

ws_id    = latest_ws["id"]
ws_title = latest_ws["title"]
ws_year  = latest_ws["published"][:4]
ws_lines = [l for l in latest_ws["desc"].split("\n") if l.strip()]
ws_desc  = "<br/>".join(ws_lines[:5]) or "Watch our latest workshop session above."

html = re.sub(r"<!--WORKSHOP_VIDEO_ID-->", ws_id,    html)
html = re.sub(r"<!--WORKSHOP_TITLE-->",    ws_title, html)
html = re.sub(r"<!--WORKSHOP_YEAR-->",     ws_year,  html)
html = re.sub(r"<!--WORKSHOP_DESC-->",     ws_desc,  html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Homepage webinar:  {vid_title} ({vid_id})")
print(f"Homepage workshop: {ws_title} ({ws_id})")

# ══════════════════════════════════════════════════════════════════════════════
# 3. WEBINAR ARCHIVE PAGE
# ══════════════════════════════════════════════════════════════════════════════
archive_html = ""
for yr in sorted(SEASON_PLAYLISTS.keys(), reverse=True):
    rss_videos = fetch_entries(SEASON_PLAYLISTS[yr])
    hardcoded  = WEBINAR_HARDCODED.get(yr, [])
    seen       = {v["id"] for v in rss_videos}
    extra      = [v for v in hardcoded if v["id"] not in seen]
    all_videos = extra + rss_videos

    archive_html += f'<div class="year-block">\n'
    archive_html += f'  <div class="year-heading"><span class="year-label">{yr}</span><div class="year-line"></div></div>\n'
    archive_html += '  <div class="thumb-grid">\n'
    for v in reversed(all_videos):
        thumb = f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg"
        link  = f"https://www.youtube.com/watch?v={v['id']}"
        archive_html += f'    <a class="thumb-item" href="{link}" target="_blank" rel="noopener"><img src="{thumb}" alt="{v["title"]}" loading="lazy"><p class="thumb-title">{v["title"]}</p></a>\n'
    archive_html += '  </div>\n</div>\n'

with open("webinar_details_template.html", "r", encoding="utf-8") as f:
    details = f.read()
details = re.sub(r"<!--WEBINAR_ARCHIVE-->", archive_html, details)
with open("webinar_details.html", "w", encoding="utf-8") as f:
    f.write(details)
print("Webinar archive rebuilt.")

# ══════════════════════════════════════════════════════════════════════════════
# 4. WORKSHOP ARCHIVE PAGE
# ══════════════════════════════════════════════════════════════════════════════
ws_archive_html = ""
for name, pid in WORKSHOP_PLAYLISTS.items():
    videos = fetch_entries(pid)
    if not videos:
        continue
    ws_archive_html += f'<div class="year-block">\n'
    ws_archive_html += f'  <div class="year-heading"><span class="year-label" style="font-size:1.6rem">{name}</span><div class="year-line"></div></div>\n'
    ws_archive_html += '  <div class="thumb-grid">\n'
    for v in videos:
        thumb = f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg"
        link  = f"https://www.youtube.com/watch?v={v['id']}"
        ws_archive_html += f'    <a class="thumb-item" href="{link}" target="_blank" rel="noopener"><img src="{thumb}" alt="{v["title"]}" loading="lazy"><p class="thumb-title">{v["title"]}</p></a>\n'
    ws_archive_html += '  </div>\n</div>\n'

with open("workshop_details_template.html", "r", encoding="utf-8") as f:
    ws_details = f.read()
ws_details = re.sub(r"<!--WORKSHOP_ARCHIVE-->", ws_archive_html, ws_details)
with open("workshop_details.html", "w", encoding="utf-8") as f:
    f.write(ws_details)
print("Workshop archive rebuilt.")
