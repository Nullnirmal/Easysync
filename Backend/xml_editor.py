import xml.etree.ElementTree as ET
import os

class xml_edit:

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()

    # Extract audio path
    def get_audio_path(self):
        audio = self.root.find(".//audio")
        if audio is not None and audio.get("src"):
            return audio.get("src")
        return None

    # Insert bookmarks
    def replace_bookmarks(self, times_am):
        for b in list(self.root.findall("bookmark")):
            self.root.remove(b)

        index = 0
        for i, elem in enumerate(self.root):
            if elem.tag in ("shape", "audio", "media"):
                index = i
                break

        for t in times_am:
            bm = ET.Element("bookmark", {"t": str(t)})
            self.root.insert(index, bm)
            index += 1

        ET.indent(self.tree, space="  ", level=0)
        self.tree.write(self.xml_path, encoding="utf-8", xml_declaration=True)
