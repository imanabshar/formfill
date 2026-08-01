# Formfill

A command-line tool that detects fillable lines in a PDF and writes text onto them. 

## About the Project

Many PDFs look like forms but aren't actually fillable. Instead of interactive form fields, they contain printed labels and blank lines meant to be completed by hand either by printing the document or by opening it in a PDF editor and manually placing text where each line sits. Tenancy agreements, applications, and many official templates use this format.

Filling one out once is manageable. Filling out the same template repeatedly means repeating that same manual placement every time. Formfill detects those blank lines once and records their exact positions. You can then reuse those coordinates to automatically populate the PDF using a simple JSON file.

## How It Works

Formfill works in two stages: detection and filling.

* **Detection** `detect.py` scans the PDF and identifies horizontal, vector-drawn lines that represent form fields and records each line's page, position, width, and index. Results are saved to `detected-lines.json`. Optionally, it can also generate a preview image for each page, highlighting every detected line in red and labeling it with its index, making it easy to see which line corresponds to which entry in the JSON file. 

* **Filling** Create a simple JSON file that maps each line index to the text you want to insert. `fill.py` reads your values together with `detected-lines.json`, places each value at the corresponding position, and generates a new PDF with the text filled in. The original PDF is never modified.

## Installation & Usage

### Setup

Requires Python 3.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1. Detect Lines

Scan a PDF to detect blank lines and record their positions.

```bash
python3 detect.py your-form.pdf --preview
```

This generates a `detected-lines.json` file:

```json
[
  {
    "page": 1,
    "x0": 69.1,
    "x1": 542.1,
    "y": 722.6,
    "width": 473.0,
    "index": 0
  },
  {
    "page": 1,
    "x0": 69.1,
    "x1": 300.0,
    "y": 690.2,
    "width": 230.9,
    "index": 1
  }
]
```

If `--preview` is provided, a labeled PNG is generated for each page showing every detected line and its index. Use these preview images to identify which index corresponds to each field before creating your values file.

**Options**

* `-o`, `--output` — Output JSON filename (default: `detected-lines.json`)
* `--preview` — Generate labeled preview images

### 2. Create a Values File

Using the preview images, identify the index of each field, then create a JSON file mapping those indices to the text you want to insert.

```json
{
  "0": "Iman",
  "1": "04/07/2026"
}
```

Keys correspond to the indices in `detected-lines.json`. Omit any index you don't want to fill.

### 3. Fill the PDF

Generate a new PDF with the specified values inserted.

```bash
python3 fill.py your-form.pdf detected-lines.json values.json -o filled-form.pdf
```

**Options**

* `-o`, `--output` — Output PDF filename (default: `filled-output.pdf`)

## Built With

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
&nbsp;&nbsp;
![pdfplumber](https://img.shields.io/badge/pdfplumber-4B8BBE?style=for-the-badge)
&nbsp;&nbsp;
![reportlab](https://img.shields.io/badge/reportlab-2E7D32?style=for-the-badge)
&nbsp;&nbsp;
![pypdf](https://img.shields.io/badge/pypdf-D32F2F?style=for-the-badge)
&nbsp;&nbsp;
![Pillow](https://img.shields.io/badge/Pillow-663399?style=for-the-badge)

</div>
