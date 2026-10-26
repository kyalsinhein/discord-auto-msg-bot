import os, json, time, datetime, urllib.request, urllib.error, xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
MAX_AGE_DAYS = 60
PER_CHANNEL = 2
UA = {"User-Agent": "Mozilla/5.0 weekly-video-bot"}
HOOK = os.environ.get("DISCORD_REVIEW_WEBHOOK", "").strip()

if not HOOK:
    raise SystemExit("ERROR: webhook secret is empty. Check that the secret NOTIBOT_PRIVATE exists and has a value.")

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
    time.sleep(1)

cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=MAX_AGE_DAYS)
post("**Weekly candidates.** Pick one, then run the 'publish-video' workflow with its link.")

lines = [l.split("#")[0].strip() for l in open("channels.txt").read().splitlines()]
ids = [l for l in lines if l]
sent = 0

for cid in ids:
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}", headers=UA)
        feed = ET.fromstring(urllib.request.urlopen(req).read())
    except Exception as e:
        print(f"SKIPPED {cid}: {e}")
        continue
    for entry in feed.findall("a:entry", NS)[:PER_CHANNEL]:
        published = datetime.datetime.fromisoformat(entry.find("a:published", NS).text)
        if published >= cutoff:
            post(entry.find("a:link", NS).attrib["href"])
            sent += 1

print(f"Done. Posted {sent} videos from {len(ids)} channels.")
