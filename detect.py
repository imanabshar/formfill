import argparse
import json
import pdfplumber
from PIL import ImageDraw, ImageFont

def detect_lines(pdf):
    """Detect horizontal lines from an already open pdfplumber PDF object."""
    results = []
    for page_num, page in enumerate(pdf.pages, start=1):
        for line in page.lines:
            # keep only horizontal lines (y0 and y1 are equal for them)
            if abs(line["y1"] - line["y0"]) < 1:
                x0 = round(line["x0"], 1)
                x1 = round(line["x1"], 1)
                y = round(line["y0"], 1)
                width = round(x1 - x0, 1)
                results.append({
                    "page": page_num,
                    "x0": x0,
                    "x1": x1,
                    "y": y,
                    "width": width
                })
    # pdfplumber returns lines in pdf drawing order and pdfs measures y from bottom so bigger y means closer to top
    # we sort by page asc and y desc, so resuts come out top to bottom 
    results.sort(key=lambda r: (r["page"], -r["y"])) 

    # give every line an index based on its position in the sorted list
    # values.json will use this number to know which field is which
    for i, r in enumerate(results):
        r["index"] = i

    return results


def save_preview_images(pdf, results):
    """Save one PNG per page with detected horizontal lines drawn in red, labeled with their index."""
    for page_num, page in enumerate(pdf.pages, start=1):
        img = page.to_image(resolution=150)
        for line in page.lines:
            if abs(line["y1"] - line["y0"]) < 1:
                img.draw_line(line, stroke="red", stroke_width=3)
        pil_image = img.annotated
        draw = ImageDraw.Draw(pil_image)
        scale = img.scale
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except OSError:
            font = ImageFont.load_default()
        for r in results:
            if r["page"] != page_num:
                continue
            label_x = r["x0"] * scale
            label_y = (page.height - r["y"]) * scale - 25
            draw.text((label_x, label_y), str(r["index"]), fill="blue", font=font)
        output_file = f"page_{page_num}_preview.png"
        pil_image.save(output_file)
        print(f"Saved {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect horizontal lines in a PDF and output their coordinates as JSON."
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument(
        "-o", "--output",
        default="detected-lines.json",
        help="Path to save the output JSON (default: detected-lines.json)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Also save png images with detected lines drawn in red"
    )
    
    args = parser.parse_args()

    with pdfplumber.open(args.pdf_path) as pdf:
        results = detect_lines(pdf)

        print(f"\nDetected {len(results)} horizontal lines:\n")
        for r in results:
            print(
                f"[{r['index']}] Page {r['page']} -> "
                f"x0:{r['x0']} x1:{r['x1']} y:{r['y']} width:{r['width']}"
            )

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved to {args.output}")

        if args.preview:
            print()
            save_preview_images(pdf, results)


if __name__ == "__main__":
    main()