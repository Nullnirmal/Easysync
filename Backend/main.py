import os
from Beat_detect import Beatdetector
from xml_editor import xml_edit

xml_path = r"D:\Code\APP\Beat Marker\Easysync\Resource\erika-idk.xml"

def main():

    if not os.path.exists(xml_path):
        print("[ERROR] XML not found")
        return

    project = xml_edit(xml_path)
    audio_path = project.get_audio_path()

    if not audio_path or not os.path.exists(audio_path):
        print("[ERROR] Audio not found in XML")
        return

    print("[INFO] Detecting beats...")
    detector = Beatdetector(threshold=0.75, lowpass=120, min_gap=0.085)
    times_am, _ = detector.detect(audio_path)

    print("[INFO] Writing bookmarks...")
    project.replace_bookmarks(times_am)

    print("[DONE] Updated XML successfully")

if __name__ == "__main__":
    main()

