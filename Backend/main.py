import os
from Beat_detecter import beat_detect
from xml_modify import get_audio_path,replace_bookmarks

xml_path = r"D:\Code\APP\Beat Marker\Alight-Beat-marker\Backend\Resource\test (1).xml"

def main():
    if not os.path.exists(xml_path):
        print("[ERROR] XML file not found.")
        return

    audio_path = get_audio_path(xml_path)
    if not audio_path or not os.path.exists(audio_path):
        print("[ERROR] Could not locate audio from XML.")
        return

    print("[INFO] Detecting beats...")
    times_am, _ = beat_detect(audio_path,
                              threshold=0.75,
                              lowpass=200,
                              min_gap=0.085)
    
   

    print("[INFO] Updating XML...")
    replace_bookmarks(xml_path, times_am)


    print("[DONE] XML successfully updated")

if __name__ == "__main__":
    main()
