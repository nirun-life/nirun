#  Copyright (c) 2026 NSTDA
# pylint: disable=missing-manifest-dependency,print-used
"""Generate the web-only Noto Sans WOFF2 subsets shipped by this addon."""

import argparse
import hashlib
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

LATIN_UNICODES = (
    "U+0000-007F,"
    "U+2000-206F,"
    "U+20A0-20CF,"
    "U+2190-21FF,"
    "U+2212,"
    "U+25CC,"
    "U+FEFF,"
    "U+FFFD"
)
THAI_UNICODES = "U+0E00-0E7F,U+200C-200D,U+25CC"
LATIN_REQUIRED = {ord(character) for character in "AZaz09 !?.,-"}
THAI_REQUIRED = {0x0E01, 0x0E17, 0x0E22, 0x0E32, 0x0E44}
SOURCE_SHA256 = {
    "NotoSans/NotoSans-Bold.ttf": (
        "cf382cad35e731fc4f13b1bf068c5085cd17bee2141014cc94919c140529488d"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-BoldItalic.ttf": (
        "8e03bc4b40dac226540463acf0bcab3e2812e04fff522b293b0fa818147d88e5"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-Italic.ttf": (
        "380a500e3dda76d955dadc77053227cc61149814737dc9f7d973d09415ad851f"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-Light.ttf": (
        "66fd7f79509ede9d6c00f5b94d20b3076c66fe065737efa5b7ef1d44d294f435"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-Medium.ttf": (
        "9d0511ca54de389e3ef4e8a8accdd94e6fdf73eb144f7bba2017e55924092822"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-MediumItalic.ttf": (
        "b2f76c30f04b3c9860487cb2e14828e8e79b49788a213ca6ff8319816d06e4f8"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-Regular.ttf": (
        "3be6b371cef19ed6add589bd106444ab74c9793bc812d3159298b73d00ee011c"  # pragma: allowlist secret
    ),
    "NotoSans/NotoSans-SemiBold.ttf": (
        "6a27c11bf011fbe565c4d5be9ab49d8535c7cfefeb3aa44dad5d1339f68aad1b"  # pragma: allowlist secret
    ),
    "NotoSansThai/NotoSansThai-Bold.ttf": (
        "efdc236dd6612b8d388f6d8e4bafb37a10ee3c3496002a542d1ef654de7f1445"  # pragma: allowlist secret
    ),
    "NotoSansThai/NotoSansThai-Light.ttf": (
        "5e564721b2f52107a60198d2e841113986267455d3b01761d1df91e1b0f6f04f"  # pragma: allowlist secret
    ),
    "NotoSansThai/NotoSansThai-Medium.ttf": (
        "17c569caf0baceded683a326f5d15cde89ba3a2c45d20eb914c66734ba4897f6"  # pragma: allowlist secret
    ),
    "NotoSansThai/NotoSansThai-Regular.ttf": (
        "be0f088df9f5118cf3c569fb002359b42238b88236d47e851ac5023d4ab5523f"  # pragma: allowlist secret
    ),
    "NotoSansThai/NotoSansThai-SemiBold.ttf": (
        "85d58cf6d92bca5582b28ccd619cef68754ae7090ffc5298538da80ae56836c9"  # pragma: allowlist secret
    ),
}

LATIN_FACES = (
    ("Light", 300, "normal"),
    ("Regular", 400, "normal"),
    ("Medium", 500, "normal"),
    ("SemiBold", 600, "normal"),
    ("Bold", 700, "normal"),
    ("Italic", 400, "italic"),
    ("MediumItalic", 500, "italic"),
    ("BoldItalic", 700, "italic"),
)
THAI_FACES = (
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
)


def _parse_unicodes(specification):
    unicodes = set()
    for item in specification.split(","):
        bounds = item.removeprefix("U+").split("-", maxsplit=1)
        start = int(bounds[0], 16)
        end = int(bounds[-1], 16)
        unicodes.update(range(start, end + 1))
    return unicodes


def _verify_source(source_dir, relative_path):
    source = source_dir / relative_path
    actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual_hash != SOURCE_SHA256[relative_path]:
        raise ValueError(f"{source} does not match the expected source font")
    return source


def _validate_font(path, expected_weight, required_unicodes):
    font = TTFont(path)
    available_unicodes = set(font.getBestCmap())
    missing_unicodes = required_unicodes - available_unicodes
    if missing_unicodes:
        missing = ", ".join(f"U+{value:04X}" for value in sorted(missing_unicodes))
        raise ValueError(f"{path} is missing required glyphs: {missing}")
    if font["OS/2"].usWeightClass != expected_weight:
        raise ValueError(f"{path} has an unexpected weight class")
    if "GSUB" not in font or "GPOS" not in font:
        raise ValueError(f"{path} is missing shaping tables")


def _subset_font(source, destination, unicodes, weight, required_unicodes):
    options = subset.Options()
    options.layout_features = ["*"]
    options.recalc_timestamp = False

    font = TTFont(source, recalcTimestamp=False)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=_parse_unicodes(unicodes))
    subsetter.subset(font)
    font.flavor = "woff2"

    destination.parent.mkdir(parents=True, exist_ok=True)
    font.save(destination, reorderTables=False)
    _validate_font(destination, weight, required_unicodes)


def generate(source_dir, output_dir):
    latin_sources = []
    for face, weight, style in LATIN_FACES:
        relative_source = f"NotoSans/NotoSans-{face}.ttf"
        latin_sources.append(
            (face, weight, style, _verify_source(source_dir, relative_source))
        )

    thai_sources = []
    for face, weight in THAI_FACES:
        relative_source = f"NotoSansThai/NotoSansThai-{face}.ttf"
        thai_sources.append((face, weight, _verify_source(source_dir, relative_source)))

    for subset_name in ("latin", "thai"):
        subset_dir = output_dir / subset_name
        subset_dir.mkdir(parents=True, exist_ok=True)
        for stale_font in subset_dir.glob("*.woff2"):
            stale_font.unlink()

    generated = []
    for face, weight, _style, source in latin_sources:
        destination = output_dir / "latin" / f"NotoSans-{face}-latin.woff2"
        _subset_font(source, destination, LATIN_UNICODES, weight, LATIN_REQUIRED)
        generated.append(destination)

    for face, weight, source in thai_sources:
        destination = output_dir / "thai" / f"NotoSansThai-{face}-thai.woff2"
        _subset_font(source, destination, THAI_UNICODES, weight, THAI_REQUIRED)
        generated.append(destination)

    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        required=True,
        type=Path,
        help="Directory containing the NotoSans and NotoSansThai TTF folders",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parents[1] / "static" / "src" / "fonts" / "web",
        help="Destination for generated WOFF2 subsets",
    )
    arguments = parser.parse_args()

    generated = generate(arguments.source_dir.resolve(), arguments.output_dir.resolve())
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
