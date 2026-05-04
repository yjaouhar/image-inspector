# Image Inspector

`Image Inspector` is a Python command-line tool for basic digital forensics on image files. It focuses on two types of analysis:

- extracting EXIF metadata such as GPS coordinates, camera/device information, software, and capture date
- scanning image least significant bits (LSB) to recover hidden text, including PGP public key blocks

The project is designed around the `Image-Inspector` subject requirements: inspect an image, display hidden information clearly, and optionally save the result to a report file.

## Features

- Metadata extraction from EXIF tags
- GPS coordinate decoding when latitude/longitude are present
- Camera make and model detection
- Capture date and software extraction
- LSB-based hidden text extraction
- PGP block detection inside recovered hidden text
- CLI output plus optional export to a file inside `output/`

## Project Structure

```text
image-inspector/
├── README.md
├── requirements.txt
├── output/
├── resources/
└── src/
    ├── __main__.py
    ├── cli.py
    ├── config.py
    ├── formatters.py
    ├── models.py
    └── analyzers/
        ├── metadata.py
        └── steganography.py
```

## Requirements

- Python `3.10+`
- `pip`

## Installation

Create a virtual environment and install the dependency:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Current dependency list:

- `pillow`

## Running the Tool

Because the source code is stored directly in `src/`, run the CLI with `PYTHONPATH=src`.

Show help:

```bash
PYTHONPATH=src python3 src/__main__.py --help
```

Expected help output:

```text
usage: image-inspector [-h] [-m] [-s] [-o OUTPUT] image

Welcome to Image Inspector

positional arguments:
  image                Path to the image file to inspect

options:
  -h, --help           show this help message and exit
  -m, --metadata       Extract metadata from the image
  -s, --steganography  Detect hidden data through LSB extraction
  -o, --output OUTPUT  Write the analysis result to the given file
```

## Usage

Extract metadata only:

```bash
PYTHONPATH=src python3 src/__main__.py -m resources/Canon_40D.jpg
```

Extract hidden data only:

```bash
PYTHONPATH=src python3 src/__main__.py -s resources/download.png
```

Run both analyses together:

```bash
PYTHONPATH=src python3 src/__main__.py -m -s resources/download.png
```

Save the report to a file:

```bash
PYTHONPATH=src python3 src/__main__.py -m -s -o audit-report.txt resources/download.png
```

When `-o` is used, the file is created in the `output/` directory, and the CLI also prints:

```text
Data saved in audit-report.txt
```

## Example Outputs

Metadata example with `resources/Canon_40D.jpg`:

```text
File: resources/Canon_40D.jpg
Lat/Lon: 25.958045038981435 / 4.130859874927283
Device: Canon Canon EOS 40D
Software: GIMP 2.4.5
Date: 2008:07:31 10:38:11
```

Steganography example with `resources/download.png`:

```text
File: resources/download.png
Detected Format: PGP block
-----BEGIN PGP PUBLIC KEY BLOCK-----
...
-----END PGP PUBLIC KEY BLOCK-----
```

Combined analysis example:

```text
File: resources/download.png
Lat/Lon: N/A / N/A
Device: N/A
Software: N/A
Date: N/A

File: resources/download.png
Detected Format: PGP block
-----BEGIN PGP PUBLIC KEY BLOCK-----
...
-----END PGP PUBLIC KEY BLOCK-----
```

## How It Works

### Metadata Extraction

The metadata analyzer uses Pillow to open the image and read EXIF information. It extracts:

- GPS latitude and longitude
- camera make
- camera model
- original capture date
- software tag

GPS values are converted from EXIF degree-minute-second format into decimal coordinates.

### Steganography Detection

The steganography analyzer:

1. converts the image to RGB
2. reads the least significant bit of each color channel
3. rebuilds bytes from the collected bit stream
4. extracts null-terminated printable text
5. checks whether the recovered text contains a PGP block

If a PGP block is found, the tool labels it as `PGP block`. Otherwise, it returns the recovered content as `Plain text`.

## Output Files

- All exported reports are stored in `output/`
- The filename is the value passed to `-o`
- The saved file contains the same text shown in the terminal

Example:

```bash
PYTHONPATH=src python3 src/__main__.py -s -o hidden.txt resources/download.png
```

This creates:

```text
output/hidden.txt
```

## Test Images

This repository already includes sample files in `resources/`, including:

- `Canon_40D.jpg`
- `Gemini_Generat.png`
- `Picsart_25-12-06_08-08-24-106.jpg`
- `anbyov.jpg`
- `download.png`

Based on the current implementation, `resources/download.png` is a useful demo image because it contains a detectable PGP public key block in its LSB stream.

## Limitations

- Steganography detection is currently limited to basic LSB extraction
- The tool only extracts text-based hidden content
- Non-text payloads are not decoded
- Some images may return noisy printable characters if their LSB data does not contain a clean hidden message
- Metadata extraction depends on EXIF availability; PNG files or stripped images may return `N/A`

## Ethical and Legal Use

Use this tool only on images you own or on images you are explicitly authorized to inspect.

- Hidden metadata may expose private locations, device details, and timelines
- Steganography analysis may reveal sensitive or confidential information
- Inspecting third-party files without permission can violate privacy rules, internal policy, or the law

This project is for educational and defensive learning purposes only.

## Audit Preparation

If you are asked to explain the project during an audit, be ready to cover:

- what EXIF metadata is and why it matters in digital forensics
- how GPS coordinates are stored in image metadata
- how LSB steganography works
- why a null-terminated hidden message can be reconstructed from image bits
- how your tool distinguishes a generic hidden text payload from a PGP block

## Submission Checklist

- `README.md`
- source code in `src/`
- dependency file `requirements.txt`
- any sample output files inside `output/`
