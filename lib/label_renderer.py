"""
Basket Case Grocer — Prepared Foods Label Sheet Generator (OL9016WJ)
=====================================================================

Builds a print-ready 9-up label sheet sized EXACTLY to the OL9016WJ dieline.
Print the resulting PDF at "Actual Size" / 100% (NEVER "Fit to Page") and the
content lands inside the die-cuts.

HOW TO MAKE NEW LABELS FOR A NEW PRODUCT
-----------------------------------------
1. Open this file in any text editor (TextEdit, VS Code, Notepad).
2. Edit the three lines below labeled "## EDIT THIS PER PRODUCT".
3. Save the file.
4. Run:    python3 build_label_sheet.py
5. Open the new PDF and print it.

The sheet currently prints all 9 labels with the SAME product info. If you
want different products on the same sheet, edit the loops at the bottom of
this file (search for "build_sheet").

Layout (extracted from sticker-sheet-1_dieline.pdf):
  6 vertical labels at top:    x=0.1808, 1.5140, 2.9083, 4.3026, 5.6969, 7.0912 in.,
                               y=0.3157 in.,  w=1.2280 in., h=6.0104 in.
  3 horizontal labels at bottom: x=1.0677 in., w=6.0104 in., h=1.2280 in.,
                                 y=6.5659, 8.0326, 9.4994 in.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# -- Brand font: Faraz Modern --
# Looks for fonts/Faraz-Regular.ttf in same folder as this script and registers
# it as "FarazModern". If missing, falls back to Times-Bold for titles.
_HERE = os.path.dirname(os.path.abspath(__file__)) or "."
# Project root assets/ folder (this file lives in lib/, assets/ is a sibling).
_PROJECT_ROOT = os.path.dirname(_HERE)
_ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")

TITLE_FONT = "Times-Bold"   # fallback
BODY_FONT  = "Helvetica"
BODY_ITALIC = "Helvetica-Oblique"
BODY_BOLD = "Helvetica-Bold"
_font_candidates = [
    os.path.join(_ASSETS_DIR, "Faraz-Regular.ttf"),
    os.path.join(_ASSETS_DIR, "fonts", "Faraz-Regular.ttf"),
    os.path.join(_HERE, "fonts", "Faraz-Regular.ttf"),
    os.path.join(_HERE, "Faraz-Regular.ttf"),
]
for fp in _font_candidates:
    if os.path.isfile(fp):
        try:
            pdfmetrics.registerFont(TTFont("FarazModern", fp))
            TITLE_FONT = BODY_FONT = BODY_ITALIC = BODY_BOLD = "FarazModern"
            break
        except Exception as e:
            print(f"[warn] couldn't register Faraz from {fp}: {e}")

# =============================================================
# ## EDIT THIS PER PRODUCT ##
# =============================================================
PRODUCT_NAME = "CHARRED LEMON AND PARSLEY POTATO SALAD"
INGREDIENTS  = "Potato, Dijon, Parsley, Lemon, Olive Oil, Garlic, Capers, Salt, Pepper"
PRICE        = ""   # e.g. "$9"  or  "$12.50"  — leave "" to omit
ALLERGENS    = ""   # leave empty if you want to skip; otherwise e.g. "Contains: nuts, eggs"
# =============================================================

# Always-on store info shown above the logo on the long edge of the label
MADE_BY_LINE_1 = "Made By: Basket Case Grocer"
MADE_BY_LINE_2 = "1801 5th Ave N Nashville"

# Logo: if a file named basket_case_logo.png (or .jpg) exists in the same
# folder as this script, the script uses it. Otherwise it falls back to the
# text wordmark below.
LOGO_FILENAMES = ["basket_case_logo.png", "basket_case_logo.jpg", "basket_case_logo.jpeg"]
BRAND_LINE_1 = "BASKET CASE"
BRAND_LINE_2 = "GROCER"

# -- Colors --
INK           = HexColor("#2C2C2C")
ACCENT        = HexColor("#5A6B47")
BORDER        = HexColor("#2C2C2C")
DIELINE_GUIDE = HexColor("#E8E4DC")

# Background: None = no fill (label paper shows through, prints fastest, saves ink).
# Set to e.g. HexColor("#FAF7F2") if you want a cream wash behind every label.
BG_CREAM      = None

# Set True to draw faint dieline outlines on the page (alignment debugging).
# Leave False for production printing.
SHOW_DIELINE = False

# Vertical label positions (top-left x in inches; all at y=0.3157)
VERT_X = [0.1808, 1.5140, 2.9083, 4.3026, 5.6969, 7.0912]
VERT_Y = 0.3157
VERT_W = 1.2280
VERT_H = 6.0104

# Horizontal label positions
HORIZ_X = 1.0677
HORIZ_W = 6.0104
HORIZ_H = 1.2280
HORIZ_Y = [6.5659, 8.0326, 9.4994]

# Internal landmarks (in inches, measured from label's top-left)
V_TOP_RECT_END   = 3.00   # bottom of the wide top rectangle
V_BOTTOM_RECT_TOP = 4.50  # top of the small bottom rectangle

# For horizontal labels (rotated equivalent)
H_LEFT_RECT_END   = 3.00
H_RIGHT_RECT_START = 4.50  # tweaked from 4.75 so logo box has more room and matches narrowest part better

# ---- Test-print fine-tune knobs (after holding a print up to a blank sheet) ----
# Positive LOGO_SHIFT_RIGHT moves the logo art toward the right end of the
# small-square (toward where "BASKET CASE" wordmark would land).
LOGO_SHIFT_RIGHT = 0.15  # inches  (was 0.10)

# Positive LOGO_SHIFT_UP moves the logo art toward the top of the small square.
# Increase if the wine-bottle cap is getting clipped at the top of the print.
LOGO_SHIFT_UP = 0.05  # inches

# Inner margin around the logo image inside its box. Bigger = smaller logo
# with more breathing room. Helps prevent edge clipping when the printer
# shifts content slightly off the die-cuts.
LOGO_INNER_MARGIN = 0.15  # inches  (was hardcoded 0.10)

# Positive TEXT_SHIFT_RIGHT pushes ALL printed text (title, ingredients,
# Made By) toward the right end of the printable info rectangle. Increase if
# the text is hugging the left edge of the die-cut on the printed sticker.
TEXT_SHIFT_RIGHT = 0.225  # inches  (was 0.10; +1/8" per test print measurement)

# How far inside the right edge of the writable region the PRICE sits.
# Increase if the price gets cut off on the right edge of the printed sticker.
# Title auto-shrinks to leave room for the price+inset.
PRICE_INSET_FROM_RIGHT = 0.20  # inches

# How far up from the bottom edge of the info area the "Made By" block sits.
# Increase if the address line gets cut off at the bottom of the printed label.
MADE_BY_UP_FROM_BOTTOM = 0.22  # inches  (was effectively ~0.10)

# Vertical gap (in points) between the last ingredient line and the Made By
# block. Reduce to pull Made By closer to the ingredients.
MADE_BY_GAP_ABOVE = 2  # points (was 4)


def in_to_pt(v):
    return v * inch


def _wrap_text(c, text, font_name, font_size, max_width):
    """Wrap a comma-delimited string into lines that fit within max_width."""
    words = text.split(", ")
    lines = []
    cur = ""
    for w_ in words:
        candidate = (cur + ", " + w_) if cur else w_
        if c.stringWidth(candidate, font_name, font_size) <= max_width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def _render_info_block(c, info_w, info_h, pad=0.10):
    """
    Render product info into a rectangle of size info_w x info_h (in points).
    Origin (0,0) is the bottom-left of the info rectangle.
    Text reads left-to-right, top-to-bottom (no rotation handled here — caller
    rotates the canvas if needed).

    Layout:
      [PRODUCT NAME — bold serif, all caps]
      [Ingredients — small sans, wrapped]
      [Contains: allergens — italic accent, optional]
      [Made By: store info — small italic, bottom of block]
    """
    # Apply TEXT_SHIFT_RIGHT — pushes all text right, eats into available width.
    shift = TEXT_SHIFT_RIGHT * inch
    inner_w = info_w - 2 * pad * inch - shift
    x0 = pad * inch + shift
    y_top = info_h - pad * inch  # top of the writable region

    # ---- Bottom-anchored: Made By store info ----
    # made_y is how far up from the very bottom of the info area the address line sits.
    # We pull it up by MADE_BY_UP_FROM_BOTTOM so it doesn't get clipped by the
    # neck cut on the actual sticker.
    made_size = 5.5
    made_h = made_size + 1.5
    made_y = MADE_BY_UP_FROM_BOTTOM * inch
    c.setFont(BODY_FONT, made_size)
    c.setFillColor(INK)
    # Line 2 sits at made_y, line 1 just above it
    c.drawString(x0, made_y, MADE_BY_LINE_2)
    c.drawString(x0, made_y + made_h, MADE_BY_LINE_1)
    bottom_anchor = made_y + made_h * 2 + MADE_BY_GAP_ABOVE

    # ---- Top-anchored: Product name + price (same line) + ingredients ----
    cur_y = y_top
    # Right edge for drawing the price (inset from the writable region's right edge)
    price_inset_pt = PRICE_INSET_FROM_RIGHT * inch
    price_right_edge = x0 + inner_w - price_inset_pt
    # Reserve room on the right for the price (drawn right-aligned on title line).
    name_size = 11
    if PRICE:
        price_w = c.stringWidth(PRICE, TITLE_FONT, name_size) + 6 + price_inset_pt  # 6pt gutter
    else:
        price_w = 0
    title_avail = inner_w - price_w
    # Auto-shrink the title to fit alongside the price.
    while c.stringWidth(PRODUCT_NAME, TITLE_FONT, name_size) > title_avail and name_size > 7.5:
        name_size -= 0.5
        if PRICE:
            price_w = c.stringWidth(PRICE, TITLE_FONT, name_size) + 6 + price_inset_pt
            title_avail = inner_w - price_w
    c.setFont(TITLE_FONT, name_size)
    c.setFillColor(INK)
    if c.stringWidth(PRODUCT_NAME, TITLE_FONT, name_size) <= title_avail:
        cur_y -= name_size
        c.drawString(x0, cur_y, PRODUCT_NAME)
        if PRICE:
            c.drawRightString(price_right_edge, cur_y, PRICE)
    else:
        # Word-wrap product name to up to 2 lines; price goes on FIRST line, right-aligned
        words = PRODUCT_NAME.split()
        lines = []
        cur = ""
        for w_ in words:
            cand = (cur + " " + w_) if cur else w_
            # First line shares width with price; second line gets full width minus price inset
            limit = title_avail if not lines else (inner_w - price_inset_pt)
            if c.stringWidth(cand, TITLE_FONT, name_size) <= limit:
                cur = cand
            else:
                if cur: lines.append(cur)
                cur = w_
        if cur: lines.append(cur)
        for i, ln in enumerate(lines[:2]):
            cur_y -= name_size
            c.drawString(x0, cur_y, ln)
            if i == 0 and PRICE:
                c.drawRightString(price_right_edge, cur_y, PRICE)
            cur_y -= 1
    cur_y -= 4

    # Ingredients — body font, wrapped
    ing_size = 6.5
    line_h = ing_size + 1.5
    lines = _wrap_text(c, INGREDIENTS, BODY_FONT, ing_size, inner_w)
    c.setFont(BODY_FONT, ing_size)
    for ln in lines:
        if cur_y - line_h < bottom_anchor:
            break  # don't run into Made By block
        cur_y -= line_h
        c.drawString(x0, cur_y, ln)

    # Allergens (optional) — italic, accent color
    if ALLERGENS:
        cur_y -= 4
        if cur_y > bottom_anchor:
            c.setFont(BODY_ITALIC, 6.5)
            c.setFillColor(ACCENT)
            c.drawString(x0, cur_y, ALLERGENS)


def _find_logo_path():
    """Return absolute path to the brand logo image if one exists, else None.
    Searches the project assets/ folder, the script folder, and assets/fonts/."""
    search_roots = [_ASSETS_DIR, _HERE]
    for root in search_roots:
        for fn in LOGO_FILENAMES:
            p = os.path.join(root, fn)
            if os.path.isfile(p):
                return p
    return None


def _render_logo_block(c, box_w, box_h):
    """Render brand block into a (box_w x box_h) rectangle.
    Origin (0,0) is bottom-left. Uses an image file if present, otherwise
    falls back to a wordmark (BASKET CASE / GROCER text)."""
    inset = 0.06 * inch
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.rect(inset, inset, box_w - 2 * inset, box_h - 2 * inset, stroke=1, fill=0)

    logo = _find_logo_path()
    if logo:
        # Fit image inside the box with an inner margin, preserving aspect.
        from reportlab.lib.utils import ImageReader
        img = ImageReader(logo)
        iw, ih = img.getSize()
        margin = LOGO_INNER_MARGIN * inch
        avail_w = box_w - 2 * margin
        avail_h = box_h - 2 * margin
        scale = min(avail_w / iw, avail_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        # Center, then nudge by the test-print knobs
        cx = box_w / 2 - draw_w / 2 + LOGO_SHIFT_RIGHT * inch
        cy = box_h / 2 - draw_h / 2 + LOGO_SHIFT_UP * inch
        # Clamp so we never push the image past the box edges (prevents
        # the wine cap / right edge of the basket from getting cut by the die-cut)
        cx = max(margin, min(cx, box_w - margin - draw_w))
        cy = max(margin, min(cy, box_h - margin - draw_h))
        c.drawImage(logo, cx, cy, width=draw_w, height=draw_h,
                    preserveAspectRatio=True, mask='auto')
        return

    # Fallback wordmark
    c.setFillColor(INK)
    name_size = 9
    while c.stringWidth(BRAND_LINE_1, "Helvetica-Bold", name_size) > box_w - 4*inset and name_size > 6:
        name_size -= 0.5
    c.setFont("Helvetica-Bold", name_size)
    c.drawCentredString(box_w / 2, box_h / 2 + 1, BRAND_LINE_1)
    c.setFont("Helvetica", 6)
    c.drawCentredString(box_w / 2, box_h / 2 - 8, BRAND_LINE_2)


def _draw_horizontal_layout(c, label_w_pt, label_h_pt):
    """
    Render horizontal-style label content at canvas origin (bottom-left).
    Layout: info area on the LEFT, logo on the RIGHT, neck (gap) in the middle.
    Caller is responsible for translating + (optionally) rotating the canvas.

    Used by both:
      - draw_horizontal_label() directly (no rotation)
      - draw_vertical_label() with a 90° CW transform, so vertical labels print
        as horizontal-layout-rotated-90°. After the user peels & rotates 90° CCW
        when applying to a container, both label types end up identical:
        title on physical top reading L→R, logo on physical right.
    """
    left_rect_w_pt  = H_LEFT_RECT_END * inch
    right_rect_w_pt = label_w_pt - H_RIGHT_RECT_START * inch

    if BG_CREAM is not None:
        c.setFillColor(BG_CREAM)
        c.rect(0, 0, left_rect_w_pt, label_h_pt, stroke=0, fill=1)
        c.rect(H_RIGHT_RECT_START * inch, 0, right_rect_w_pt, label_h_pt, stroke=0, fill=1)

    # Left rectangle: product info
    c.saveState()
    _render_info_block(c, info_w=left_rect_w_pt, info_h=label_h_pt)
    c.restoreState()

    # Right small rectangle: logo
    c.saveState()
    c.translate(H_RIGHT_RECT_START * inch, 0)
    _render_logo_block(c, box_w=right_rect_w_pt, box_h=label_h_pt)
    c.restoreState()


def draw_horizontal_label(c, x, y, w, h):
    """Horizontal (landscape) label, drawn upright. (x, y) top-left in topdown inches."""
    page_h_pt = letter[1]
    label_bottom_pt = page_h_pt - (y + h) * inch
    label_left_pt   = x * inch

    c.saveState()
    c.translate(label_left_pt, label_bottom_pt)
    _draw_horizontal_layout(c, w * inch, h * inch)
    c.restoreState()


def draw_vertical_label(c, x, y, w, h):
    """
    Vertical (portrait) label rendered as horizontal layout pre-rotated 90° CW.

    Why: when applied to a container with the long edge horizontal, the user
    rotates the peeled label 90° CCW. The pre-rotation cancels, so the result
    matches horizontal labels: title on physical top reading L→R, logo on
    physical right side, "Made By" on physical bottom.

    The h x w of the vertical label (1.228" w × 6.0104" h) becomes
    a horizontal layout of (h × w) (= 6.0104" wide × 1.228" tall) drawn
    rotated 90° CW into the vertical label's PDF rectangle.
    """
    page_h_pt = letter[1]
    label_bottom_pt = page_h_pt - (y + h) * inch
    label_left_pt   = x * inch
    w_pt = w * inch
    h_pt = h * inch

    c.saveState()
    # Place ourselves at vertical label's bottom-left in PDF coords.
    c.translate(label_left_pt, label_bottom_pt)
    # Now apply a transform such that drawing in the (h_pt × w_pt) horizontal-
    # layout coordinate space lands inside the (w_pt × h_pt) vertical rectangle.
    # Math: translate(0, h_pt) then rotate(-90) maps horizontal block (xh, yh)
    # to vertical PDF (yh, h_pt - xh). Verified at all four corners.
    c.translate(0, h_pt)
    c.rotate(-90)
    _draw_horizontal_layout(c, h_pt, w_pt)
    c.restoreState()


def draw_dieline_outline_for_label(c, x, y, w, h, vertical=True):
    """Optional: draw a faint dieline outline matching the actual die-cut shape."""
    page_h_pt = letter[1]
    c.setStrokeColor(DIELINE_GUIDE)
    c.setLineWidth(0.3)
    if vertical:
        bottom_y = page_h_pt - (y + h) * inch
        # Top rectangle outline
        c.rect(x*inch, bottom_y + (h - V_TOP_RECT_END)*inch,
               w*inch, V_TOP_RECT_END*inch, stroke=1, fill=0)
        # Bottom rectangle outline
        c.rect(x*inch, bottom_y, w*inch, (h - V_BOTTOM_RECT_TOP)*inch,
               stroke=1, fill=0)
    else:
        bottom_y = page_h_pt - (y + h) * inch
        # Left rectangle (info)
        c.rect(x*inch, bottom_y, H_LEFT_RECT_END*inch, h*inch, stroke=1, fill=0)
        # Right rectangle (logo)
        c.rect((x + H_RIGHT_RECT_START)*inch, bottom_y,
               (w - H_RIGHT_RECT_START)*inch, h*inch, stroke=1, fill=0)


def build_sheet(out_path):
    c = canvas.Canvas(out_path, pagesize=letter)
    c.setTitle("Basket Case Grocer — OL9016WJ Prepared Foods Labels")

    # 6 vertical labels at top
    for vx in VERT_X:
        if SHOW_DIELINE:
            draw_dieline_outline_for_label(c, vx, VERT_Y, VERT_W, VERT_H, vertical=True)
        draw_vertical_label(c, vx, VERT_Y, VERT_W, VERT_H)

    # 3 horizontal labels at bottom
    for hy in HORIZ_Y:
        if SHOW_DIELINE:
            draw_dieline_outline_for_label(c, HORIZ_X, hy, HORIZ_W, HORIZ_H, vertical=False)
        draw_horizontal_label(c, HORIZ_X, hy, HORIZ_W, HORIZ_H)

    c.showPage()
    c.save()
    print(f"Wrote: {out_path}")


def safe_filename(s):
    return "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "_" for ch in s).strip().replace(" ", "_")


def build_sheet_bytes(product_name, ingredients, price="", allergens=""):
    """Library entry point used by the web service.

    Renders one 9-up sheet using the provided fields and returns the PDF bytes.
    Applies the same Faraz Modern '&' kerning fix and price-with-or-without-$
    tolerance the desktop CLI uses.
    """
    import io
    global PRODUCT_NAME, INGREDIENTS, PRICE, ALLERGENS

    # Normalize price: tolerate both "$9" and "9"; prepend $ if missing.
    p = (price or "").strip()
    if p and not p.startswith("$") and any(ch.isdigit() for ch in p):
        p = "$" + p

    # Apply Faraz Modern '&' kerning fix (replace & with 'and') in BOTH title
    # and ingredients before rendering. Same convention as the cabinet kit.
    def fix(s):
        return (s or "").replace("&", "and").replace("  ", " ").strip()

    PRODUCT_NAME = fix(product_name).upper()
    INGREDIENTS = fix(ingredients)
    PRICE = p
    ALLERGENS = fix(allergens)

    buf = io.BytesIO()
    build_sheet(buf)
    return buf.getvalue()


if __name__ == "__main__":
    import sys
    # Local CLI for testing the library form.
    here = os.path.dirname(os.path.abspath(__file__)) or "."
    name = sys.argv[1] if len(sys.argv) > 1 else PRODUCT_NAME
    ing  = sys.argv[2] if len(sys.argv) > 2 else INGREDIENTS
    pr   = sys.argv[3] if len(sys.argv) > 3 else PRICE
    pdf_bytes = build_sheet_bytes(name, ing, pr)
    out = os.path.join(here, f"Basket_Case_Labels_{safe_filename(name)}.pdf")
    with open(out, "wb") as f:
        f.write(pdf_bytes)
    print(f"\nDone. Open {out} and print at 'Actual Size' (100%).")
