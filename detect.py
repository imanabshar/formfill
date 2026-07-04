import argparse
import json
import pdfplumber

def detect_lines(pdf_path):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_height = page.height

            for line in page.lines:

                # keep only horizontal lines (y0 and y1 are equal for them)
                if abs(line["y1"] - line["y0"]) < 1:
                    x0 = round(line["x0"], 1)
                    x1 = round(line["x1"], 1)

                    # flipping the y-coords because pdf coordinate system has origin at bottom-left
                    y = round(page_height - line["y0"], 1)
                    width = round(x1 - x0, 1)

                    results.append({
                        "page": page_num,
                        "x0": x0,
                        "x1": x1,
                        "y": y,
                        "width": width
                    })

    # sort by page and y as pdfplumber returns lines in pdf drawing order
    # not necessarily top to bottom, so we are fixing that here 
    results.sort(key=lambda r: (r["page"], r["y"])) 
    return results


def save_preview_images(pdf_path):
    """Save one PNG per page with detected horizontal lines drawn in red."""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            img = page.to_image(resolution=150)

            for line in page.lines:
                if abs(line["y1"] - line["y0"]) < 1:
                    img.draw_line(line, stroke="red", stroke_width=3)

            output_file = f"page_{page_num}_preview.png"
            img.save(output_file)
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

    results = detect_lines(args.pdf_path)

    print(f"\nDetected {len(results)} horizontal lines:\n")
    for r in results:
        print(
            f"Page {r['page']} -> "
            f"x0:{r['x0']} x1:{r['x1']} y:{r['y']} width:{r['width']}"
        )

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {args.output}")

    if args.preview:
        print()
        save_preview_images(args.pdf_path)


if __name__ == "__main__":
    main()