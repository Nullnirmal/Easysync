import xml.etree.ElementTree as ET

def get_audio_path(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    audio = root.find(".//audio")
    if audio is not None and audio.get("src"):
        return audio.get("src").replace("file://", "").strip()

    for media in root.findall(".//media"):
        if "audio" in media.get("type", "").lower():
            if media.get("uri"):
                return media.get("uri").replace("file://", "").strip()

    return None


def replace_bookmarks(xml_path, times_am):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for b in list(root.findall("bookmark")):
        root.remove(b)

    insert_index = 0
    for i, elem in enumerate(root):
        if elem.tag in ("shape", "audio", "media"):
            insert_index = i
            break

    for t in times_am:
        bookmark = ET.Element("bookmark", {"t": str(t)})
        root.insert(insert_index, bookmark)
        insert_index += 1

    ET.indent(tree, space="  ", level=0)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    print(f"[XML] Inserted {len(times_am)} bookmarks ✅")
