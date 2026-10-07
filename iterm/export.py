#!/usr/bin/env python3
"""Export only iTerm profile appearance; leave the live preferences untouched."""
import argparse
import json
from pathlib import Path
import plistlib
import re
import uuid

COLOR = re.compile(
    r"(?:Ansi (?:[0-9]|1[0-5])|Background|Badge|Bold|Cursor|Cursor Guide|"
    r"Cursor Text|Foreground|Link|Selected Text|Selection) Color(?: \((?:Dark|Light)\))?"
)
COLOR_COMPONENTS = {"Red Component", "Green Component", "Blue Component", "Alpha Component"}
NUMERIC = {
    "Horizontal Spacing", "Vertical Spacing", "Transparency", "Blur Radius",
    "Cursor Type", "Minimum Contrast", "Faint Text Alpha", "Cursor Boost",
}
BOOLEAN = {
    "ASCII Anti Aliased", "Non-ASCII Anti Aliased", "Use Bold Font",
    "Use Italic Font", "Use Non-ASCII Font", "Use Separate Colors for Light and Dark Mode",
    "Blinking Cursor", "Blur", "Use Bright Bold", "Brighten Bold Text",
    "Smart Cursor Color", "Use Cursor Guide", "Use Selected Text Color",
}


def export_profiles(preferences):
    profiles = []
    for source in preferences.get("New Bookmarks", []):
        # Different GUIDs let these coexist with the original regular profiles.
        source_id = source["Guid"]
        result = {
            "Name": source["Name"] + " (portable)",
            "Guid": str(uuid.uuid5(uuid.NAMESPACE_URL, "grantcko/dotfiles/iterm/" + source_id)),
        }
        for key, value in source.items():
            base = re.sub(r" \((?:Dark|Light)\)$", "", key)
            if COLOR.fullmatch(key) and isinstance(value, dict):
                color = {k: v for k, v in value.items()
                         if k in COLOR_COMPONENTS and type(v) in (int, float)}
                if value.get("Color Space") in ("sRGB", "Calibrated", "P3"):
                    color["Color Space"] = value["Color Space"]
                if color:
                    result[key] = color
            elif base in NUMERIC and type(value) in (int, float):
                result[key] = value
            elif base in BOOLEAN and type(value) is bool:
                result[key] = value
            elif key in {"Normal Font", "Non Ascii Font"} and isinstance(value, str):
                if re.fullmatch(r"[\w .-]+ [0-9]+(?:\.[0-9]+)?", value):
                    result[key] = value
        profiles.append(result)
    return {"Profiles": profiles}


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=here.parent / "com.googlecode.iterm2.plist")
    parser.add_argument("--output", type=Path, default=here / "profiles.json")
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("output must differ from the live preferences source")
    result = export_profiles(plistlib.loads(args.source.read_bytes()))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Exported appearance for {len(result['Profiles'])} profiles to {args.output}")


if __name__ == "__main__":
    main()
