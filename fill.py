import argparse      
import json          
import io            
from pypdf import PdfReader, PdfWriter   
from reportlab.pdfgen import canvas      
from reportlab.pdfbase.pdfmetrics import stringWidth


DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
MIN_FONT_SIZE = 6


def fit_font_size(text, max_width, font_name=DEFAULT_FONT, start_size=DEFAULT_FONT_SIZE, min_size=MIN_FONT_SIZE):
    """Return the largest font size (down to min_size) at which text fits within max_width."""

    size = start_size
    while size > min_size:
        width = stringWidth(text, font_name, size)
        if width <= max_width:
            return size
        size -= 1
    return min_size


def build_overlays(pdf_path, detected_lines, field_values, font_size=DEFAULT_FONT_SIZE):
    """Create one blank page with text drawn on it per PDF page that needs filling."""

    reader = PdfReader(pdf_path)  
    overlays = {} 

    for index_str, text in field_values.items():
        index = int(index_str)  

        # if user typed an index that doesn't exist in detected-lines we skip it
        if index >= len(detected_lines):
            print(f"Warning: index {index} has no matching detected line, skipping")
            continue

        line = detected_lines[index]   
        page_num = line["page"]        

        if page_num not in overlays:
            page = reader.pages[page_num - 1]  # pypdf counts pages from 0 our page num starts at 1
            page_width = float(page.mediabox.width)    
            page_height = float(page.mediabox.height)   

            buffer = io.BytesIO()  

            overlays[page_num] = {
                "buffer": buffer,
                "canvas": canvas.Canvas(buffer, pagesize=(page_width, page_height))
            }

        # shrink font to fit the line's width if the text is too long at the default size
        max_width = line["width"]
        fitted_size = fit_font_size(text, max_width, DEFAULT_FONT, font_size, MIN_FONT_SIZE)
        if fitted_size < font_size:
            print(
                f"Note: shrinking font for index {index} ('{text}') "
                f"to {fitted_size}pt to fit line width {max_width}"
            )

        overlays[page_num]["canvas"].setFont(DEFAULT_FONT, fitted_size)
        overlays[page_num]["canvas"].drawString(line["x0"], line["y"] + 2, text)

    for page_num in overlays:
        overlays[page_num]["canvas"].save()     
        overlays[page_num]["buffer"].seek(0)    

    return overlays 


def fill_pdf(pdf_path, detected_lines, field_values, output_path, font_size=DEFAULT_FONT_SIZE):
    reader = PdfReader(pdf_path)   
    writer = PdfWriter()           

    overlays = build_overlays(pdf_path, detected_lines, field_values, font_size) 

    for i, page in enumerate(reader.pages, start=1):
        if i in overlays:
            overlay_reader = PdfReader(overlays[i]["buffer"])
            # stack overlay's text on top of the real page
            page.merge_page(overlay_reader.pages[0])

        # add this page (with or w/o new text) to our final output
        writer.add_page(page)

    with open(output_path, "wb") as f: 
        writer.write(f)


def main():
    parser = argparse.ArgumentParser(
        description="Fill a PDF's detected lines with text, based on a values JSON file."
    )
    parser.add_argument("pdf_path", help="Path to the original PDF file")
    parser.add_argument("detected_json", help="Path to detected-lines.json from detect.py")
    parser.add_argument("values_json", help="Path to a JSON file mapping line index to text")
    parser.add_argument(
        "-o", "--output",
        default="output.pdf",
        help="Path to save the filled PDF (default: filled-output.pdf)"
    )
    parser.add_argument(
        "-f", "--font-size",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help=f"Starting font size before auto-shrink kicks in (default: {DEFAULT_FONT_SIZE})"
    )

    args = parser.parse_args() 

    with open(args.detected_json) as f:

        detected_lines = json.load(f)   

    with open(args.values_json) as f:
        field_values = json.load(f)   
        
    fill_pdf(args.pdf_path, detected_lines, field_values, args.output, args.font_size)
    print(f"Saved filled PDF to {args.output}")


if __name__ == "__main__":
    main()