import re
import urllib.request
import xml.etree.ElementTree as ET

SEASON_PLAYLISTS = {
    "2022": "PLSGSXuijkB6nllG5-O4U1Ut2dslgjiG5Q",
    "2023": "PLSGSXuijkB6l7xcbZfFBJLVnkkrQ8FiRi",
    "2024": "PLSGSXuijkB6mldY54HJy109_CJZ19WYiN",
    "2025": "PLSGSXuijkB6lVfGionx2m8e5h2czsX0oM",
    "2026": "PLSGSXuijkB6lLMe8sZ3fDkReWrH_5HdWC",
}

HARDCODED = {
    "2022": [
        {"id": "y2FTkbNrVsw", "title": "Introductory Session"},
        {"id": "UN4AOWvf-cg", "title": "Clouds as we measure and understand"},
    ]
}

ns = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt":   "http://www.youtube.com/xml/schemas/2015",
    "media":"http://search.yahoo.com/mrss/"
}

def fetch_playlist_entries(playlist_id):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        xml_data = r.read()
    root = ET.fromstring(xml_data)
    entries = root.findall("atom:entry", ns)
    result = []
    for e in entries:
        vid   = e.find("yt:videoId", ns).text
        title = e.find("atom:title", ns).text
        result.append({"id": vid, "title": title})
    return result

# ── Homepage: latest video from 2026 ──────────────────────────────────────────
latest = fetch_playlist_entries(SEASON_PLAYLISTS["2026"])
entry  = latest[0]
video_id = entry["id"]
title    = entry["title"]

media_desc = ""
url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={SEASON_PLAYLISTS['2026']}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as r:
    root2 = ET.fromstring(r.read())
first_entry = root2.findall("atom:entry", ns)[0]
published   = first_entry.find("atom:published", ns).text
year        = published[:4]
media_group = first_entry.find("media:group", ns)
description = media_group.find("media:description", ns).text or ""
lines       = [l for l in description.split("\n") if l.strip()]
description_html = "<br/>".join(lines[:5])

with open("index_template.html", "r", encoding="utf-8") as f:
    html = f.read()
html = re.sub(r"<!--WEBINAR_VIDEO_ID-->", video_id, html)
html = re.sub(r"<!--WEBINAR_TITLE-->",    title,    html)
html = re.sub(r"<!--WEBINAR_YEAR-->",     year,     html)
html = re.sub(r"<!--WEBINAR_DESC-->",     description_html, html)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# ── Archive: thumbnail grid, 4 per row, newest year first ────────────────────
archive_html = ""
for yr in sorted(SEASON_PLAYLISTS.keys(), reverse=True):
    rss_videos = fetch_playlist_entries(SEASON_PLAYLISTS[yr])

    # Merge hardcoded (oldest) + RSS, deduplicate by video id
    hardcoded  = HARDCODED.get(yr, [])
    seen       = {v["id"] for v in rss_videos}
    extra      = [v for v in hardcoded if v["id"] not in seen]
    all_videos = extra + rss_videos   # hardcoded oldest → RSS newest

    archive_html += f'''
<div class="year-block">
  <div class="year-heading">
    <span class="year-label">{yr}</span>
    <div class="year-line"></div>
  </div>
  <div class="thumb-grid">
'''
    for v in reversed(all_videos):   # newest first in display
        thumb = f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg"
        link  = f"https://www.youtube.com/watch?v={v['id']}"
        archive_html += f'''    <a class="thumb-item" href="{link}" target="_blank" rel="noopener">
      <img src="{thumb}" alt="{v['title']}" loading="lazy">
      <p class="thumb-title">{v['title']}</p>
    </a>
'''
    archive_html += '  </div>\n</div>\n'

with open("webinar_details_template.html", "r", encoding="utf-8") as f:
    details = f.read()
details = re.sub(r"<!--WEBINAR_ARCHIVE-->", archive_html, details)
with open("webinar_details.html", "w", encoding="utf-8") as f:
    f.write(details)

print(f"Homepage: {title} ({video_id})")
print(f"Archive: {sum(len(fetch_playlist_entries(SEASON_PLAYLISTS[y])) + len(HARDCODED.get(y,[])) for y in SEASON_PLAYLISTS)} total videos across 5 seasons")
