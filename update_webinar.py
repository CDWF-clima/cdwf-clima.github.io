import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict

# Map each season playlist to its year
SEASON_PLAYLISTS = {
    "2022": "PLSGSXuijkB6nllG5-O4U1Ut2dslgjiG5Q",
    "2023": "PLSGSXuijkB6l7xcbZfFBJLVnkkrQ8FiRi",
    "2024": "PLSGSXuijkB6mldY54HJy109_CJZ19WYiN",
    "2025": "PLSGSXuijkB6lVfGionx2m8e5h2czsX0oM",
    "2026": "PLSGSXuijkB6lLMe8sZ3fDkReWrH_5HdWC",
}

ns = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/"
}

def fetch_playlist_entries(playlist_id):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()
    root = ET.fromstring(xml_data)
    return root.findall("atom:entry", ns)

# ---- Fetch the latest video overall (from the current/newest season) for the homepage card ----
latest_entries = fetch_playlist_entries(SEASON_PLAYLISTS["2026"])
entry = latest_entries[0]  # newest first in RSS

video_id = entry.find("yt:videoId", ns).text
title = entry.find("atom:title", ns).text
published = entry.find("atom:published", ns).text
year = published[:4]

media_group = entry.find("media:group", ns)
description = media_group.find("media:description", ns).text or ""
lines = [l for l in description.split("\n") if l.strip() != ""]
description = "\n".join(lines[:5])
description_html = description.replace("\n", "<br/>")

# ---- Update homepage (index.html) ----
with open("index_template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r"<!--WEBINAR_VIDEO_ID-->", video_id, html)
html = re.sub(r"<!--WEBINAR_TITLE-->", title, html)
html = re.sub(r"<!--WEBINAR_YEAR-->", year, html)
html = re.sub(r"<!--WEBINAR_DESC-->", description_html, html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# ---- Build full year-grouped archive from ALL season playlists ----
archive_html = ""
for yr in sorted(SEASON_PLAYLISTS.keys(), reverse=True):
    pid = SEASON_PLAYLISTS[yr]
    entries = fetch_playlist_entries(pid)
    if not entries:
        continue

    # RSS lists newest-added first; reverse so S1 = first added, increasing
    entries_ordered = list(reversed(entries))
    total = len(entries_ordered)

    archive_html += f'<div class="year-block">\n'
    archive_html += f'  <div class="year-heading">\n'
    archive_html += f'    <span class="year-label">{yr}</span>\n'
    archive_html += f'    <div class="year-line"></div>\n'
    archive_html += f'  </div>\n'
    archive_html += '  <div class="session-list">\n'

    # Display newest session first (highest number at top)
    for idx, e in enumerate(reversed(entries_ordered)):
        session_num = total - idx
        vid = e.find("yt:videoId", ns).text
        vtitle = e.find("atom:title", ns).text
        video_url = f"https://www.youtube.com/watch?v={vid}"
        archive_html += f'''
    <div class="session-card">
      <div class="session-num">S{session_num}</div>
      <div class="session-body">
        <p class="session-title">{vtitle}</p>
        <a class="session-link" href="{video_url}" target="_blank">
          <span class="yt-icon"></span> Watch on YouTube
        </a>
      </div>
    </div>
'''
    archive_html += '  </div>\n</div>\n'

with open("webinar_details_template.html", "r", encoding="utf-8") as f:
    details_html = f.read()

details_html = re.sub(r"<!--WEBINAR_ARCHIVE-->", archive_html, details_html)

with open("webinar_details.html", "w", encoding="utf-8") as f:
    f.write(details_html)

print(f"Homepage updated to: {title} ({video_id})")
print(f"Archive rebuilt across {len(SEASON_PLAYLISTS)} seasons")
