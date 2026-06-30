import re
import urllib.request
import xml.etree.ElementTree as ET

PLAYLIST_ID = "PLSGSXuijkB6lLMe8sZ3fDkReWrH_5HdWC"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST_ID}"

ns = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/"
}

req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as response:
    xml_data = response.read()

root = ET.fromstring(xml_data)
entry = root.find("atom:entry", ns)

video_id = entry.find("yt:videoId", ns).text
title = entry.find("atom:title", ns).text
published = entry.find("atom:published", ns).text
year = published[:4]

media_group = entry.find("media:group", ns)
description = media_group.find("media:description", ns).text or ""

lines = [l for l in description.split("\n") if l.strip() != ""]
description = "\n".join(lines[:5])
description_html = description.replace("\n", "<br/>")

# READ from the template (never overwritten)
with open("index_template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r"<!--WEBINAR_VIDEO_ID-->", video_id, html)
html = re.sub(r"<!--WEBINAR_TITLE-->", title, html)
html = re.sub(r"<!--WEBINAR_YEAR-->", year, html)
html = re.sub(r"<!--WEBINAR_DESC-->", description_html, html)

# WRITE to the live file (this is what changed)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Updated to video: {title} ({video_id})")
