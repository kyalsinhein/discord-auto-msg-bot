import os, json, time, datetime, urllib.request, xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
MAX_AGE_DAYS = 14        # ignore older uploads
PER_CHANNEL = 2          # latest N videos per channel
HOOK = os.environ["DISCORD_REVIEW_WEBHOOK"]

def post(text):
    req = urllib.request.Request(HOOK, data=json.dumps({"content": text}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "weekly-video"})
    urllib.request.urlopen(req)
    time.sleep(1)  # stay under rate limits

cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=MAX_AGE_DAYS)
post("**Weekly candidates.** Pick one, then run the 'publish-video' workflow with its link.")

for cid in open("channels.txt").read().split():
    feed = ET.fromstring(urllib.request.urlopen(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}").read())
    for e in feed.findall("a:entry", NS)[:PER_CHANNEL]:
        published = datetime.datetime.fromisoformat(e.find("a:published", NS).text)
        if published >= cutoff:
            post(e.find("a:link", NS).attrib["href"])
