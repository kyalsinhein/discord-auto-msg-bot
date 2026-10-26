import os, json, time, datetime, urllib.request, urllib.error, xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
UA = {"User-Agent": "Mozilla/5.0 weekly-video-bot"}
HOOK = os.environ.get("DISCORD_WEBHOOK", "").strip()
MAX_AGE_DAYS = 0   # 0 = always post each channel's latest video; 7 = only if uploaded in the last 7 days

if not HOOK:
    raise SystemExit("ERROR: webhook secret is empty. Check the NOTIBOT_PUBLIC secret.")

def post(text):
    req = urllib.request.Request(
        HOOK,
        data=json.dumps({"content": text}).encode(),
        headers={"Content-Type": "application/json", **UA},
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ERROR: Discord rejected the message ({e.code}). Check the webhook URL.")
    time.sleep(3)  # one by one, with a pause between videos

ids = [l.split("#")[0].strip() for l in open("channels.txt").read().splitlines()]
ids = [i for i in ids if i]
now = datetime.datetime.now(datetime.timezone.utc)
sent = 0

post("**Weekly knowledge videos**")

for cid in ids:
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}", headers=UA)
        feed = ET.fromstring(urllib.request.urlopen(req).read())
        entry = feed.find("a:entry", NS)
        link = entry.find("a:link", NS).attrib["href"]
        published = datetime.datetime.fromisoformat(entry.find("a:published", NS).text)
    except Exception as e:
        print(f"SKIPPED {cid}: {e}")
        continue
    if MAX_AGE_DAYS and (now - published).days > MAX_AGE_DAYS:
        print(f"SKIPPED {cid}: older than {MAX_AGE_DAYS} days")
        continue
    post(link)
    sent += 1

print(f"Done. Posted {sent} videos from {len(ids)} channels.")
