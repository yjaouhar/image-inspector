from __future__ import annotations

from PIL import Image

from models import SteganographyReport


PGP_BEGIN = "-----BEGIN PGP"
PGP_END = "-----END PGP"


def extract_lsb_bytes(image_path: str) -> bytes:
    with Image.open(image_path) as image:
        rgb_image = image.convert("RGB")

        # Flatten the image into a predictable RGB pixel stream.
        pixels = [rgb_image.getpixel((x, y)) for y in range(rgb_image.height) for x in range(rgb_image.width)]

    bits: list[str] = []
    for red, green, blue in pixels:
        # Read the least significant bit from each color channel.
        bits.append(str(red & 1))
        bits.append(str(green & 1))
        bits.append(str(blue & 1))

    byte_values = []
    # Ignore trailing bits that do not make a full byte.
    usable_length = len(bits) - (len(bits) % 8)
    for index in range(0, usable_length, 8):
        chunk = "".join(bits[index:index + 8])
        byte_values.append(int(chunk, 2))

    return bytes(byte_values)


def _extract_null_terminated_text(blob: bytes) -> str | None:
    # Stop at the first null byte, which is a common hidden-text terminator.
    trimmed = blob.split(b"\x00", 1)[0].strip()
    if not trimmed:
        return None

    try:
        decoded = trimmed.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to a permissive decoding pass when the payload is not valid UTF-8.
        decoded = trimmed.decode("latin-1", errors="ignore")

    # Keep only printable characters so binary noise does not pollute the output.
    cleaned = "".join(char for char in decoded if char.isprintable() or char in "\r\n\t")
    return cleaned.strip() or None


def _extract_pgp_block(text: str) -> str | None:
    # Extract only the armored PGP block when hidden text contains extra noise.
    start = text.find(PGP_BEGIN)
    if start == -1:
        return None

    end = text.find(PGP_END, start)
    if end == -1:
        return text[start:].strip()

    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    return text[start:line_end].strip()


def analyze_steganography(image_path: str) -> SteganographyReport:
    lsb_bytes = extract_lsb_bytes(image_path)

    text = _extract_null_terminated_text(lsb_bytes)

    if not text:
        return SteganographyReport(
            file_path=image_path,
            hidden_text=None,
            detected_format=None,
        )

    pgp_block = _extract_pgp_block(text)
    if pgp_block:
        return SteganographyReport(
            file_path=image_path,
            hidden_text=pgp_block,
            detected_format="PGP block",
        )

    return SteganographyReport(
        file_path=image_path,
        hidden_text=text,
        detected_format="Plain text",
    )
