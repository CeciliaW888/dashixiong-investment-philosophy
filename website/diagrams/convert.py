import json
import os
import html

DIAGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = [
    ("01-monetary-evolution.excalidraw", "01-monetary-evolution.svg"),
    ("02-gold-five-contradictions.excalidraw", "02-gold-five-contradictions.svg"),
    ("03-six-assets-network.excalidraw", "03-six-assets-network.svg"),
    ("04-three-part-method.excalidraw", "04-three-part-method.svg"),
    ("05-policy-vs-real-bull.excalidraw", "05-policy-vs-real-bull.svg"),
    ("06-china-us-financial.excalidraw", "06-china-us-financial.svg"),
]

PADDING = 20


def compute_bounding_box(elements):
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for el in elements:
        if el.get("isDeleted"):
            continue
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", 0)
        h = el.get("height", 0)

        # For arrows/lines, also consider points
        if el["type"] in ("arrow", "line"):
            for pt in el.get("points", []):
                px = x + pt[0]
                py = y + pt[1]
                min_x = min(min_x, px)
                min_y = min(min_y, py)
                max_x = max(max_x, px)
                max_y = max(max_y, py)
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

    return min_x, min_y, max_x, max_y


def dash_attr(el):
    if el.get("strokeStyle") == "dashed":
        return ' stroke-dasharray="8,4"'
    return ""


def opacity_attr(el):
    op = el.get("opacity", 100)
    if op < 100:
        return f' opacity="{op / 100}"'
    return ""


def fill_color(el):
    bg = el.get("backgroundColor", "transparent")
    if bg == "transparent" or not bg:
        return "none"
    return bg


def render_arrowhead_marker(marker_id, color):
    return (
        f'<marker id="{marker_id}" markerWidth="10" markerHeight="7" '
        f'refX="10" refY="3.5" orient="auto" markerUnits="strokeWidth">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{color}" />'
        f"</marker>"
    )


def render_element(el, offset_x, offset_y, markers):
    if el.get("isDeleted"):
        return ""

    t = el["type"]
    x = el.get("x", 0) - offset_x
    y = el.get("y", 0) - offset_y
    w = el.get("width", 0)
    h = el.get("height", 0)
    stroke = el.get("strokeColor", "#1e1e1e")
    sw = el.get("strokeWidth", 2)
    fill = fill_color(el)
    da = dash_attr(el)
    oa = opacity_attr(el)
    rx = 0
    if el.get("roundness") and el["roundness"].get("type") == 3:
        rx = 8

    if t == "rectangle":
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{da}{oa} />'
        )

    elif t == "ellipse":
        cx = x + w / 2
        cy = y + h / 2
        rx_e = w / 2
        ry_e = h / 2
        return (
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx_e}" ry="{ry_e}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{oa} />'
        )

    elif t == "diamond":
        cx = x + w / 2
        cy = y + h / 2
        points = f"{cx},{y} {x + w},{cy} {cx},{y + h} {x},{cy}"
        return (
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{da}{oa} />'
        )

    elif t == "text":
        text_content = el.get("text", "")
        font_size = el.get("fontSize", 16)
        text_color = stroke
        lines = text_content.split("\n")
        text_align = el.get("textAlign", "center")

        if text_align == "center":
            anchor = "middle"
            tx = x + w / 2
        elif text_align == "right":
            anchor = "end"
            tx = x + w
        else:
            anchor = "start"
            tx = x

        line_height = font_size * el.get("lineHeight", 1.25)
        total_text_height = line_height * len(lines)
        # Vertically center the text block within the element height
        start_y = y + (h - total_text_height) / 2 + font_size * 0.85

        parts = []
        for i, line in enumerate(lines):
            ly = start_y + i * line_height
            escaped = html.escape(line)
            parts.append(
                f'<text x="{tx}" y="{ly}" fill="{text_color}" '
                f'font-size="{font_size}" font-family="system-ui, sans-serif" '
                f'text-anchor="{anchor}"{oa}>{escaped}</text>'
            )
        return "\n".join(parts)

    elif t in ("arrow", "line"):
        points = el.get("points", [])
        if len(points) < 2:
            return ""

        marker_attr = ""
        if t == "arrow" and el.get("endArrowhead") == "arrow":
            mid = f"arrowhead-{stroke.replace('#', '')}"
            if mid not in markers:
                markers[mid] = render_arrowhead_marker(mid, stroke)
            marker_attr = f' marker-end="url(#{mid})"'

        coords = []
        for pt in points:
            px = x + pt[0]
            py = y + pt[1]
            coords.append(f"{px},{py}")

        if len(coords) == 2:
            p1 = points[0]
            p2 = points[1]
            x1 = x + p1[0]
            y1 = y + p1[1]
            x2 = x + p2[0]
            y2 = y + p2[1]
            return (
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{stroke}" stroke-width="{sw}"{da}{oa}{marker_attr} />'
            )
        else:
            pts = " ".join(coords)
            return (
                f'<polyline points="{pts}" fill="none" stroke="{stroke}" '
                f'stroke-width="{sw}"{da}{oa}{marker_attr} />'
            )

    return ""


def convert_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    elements = data.get("elements", [])
    active = [e for e in elements if not e.get("isDeleted")]
    if not active:
        print(f"  Skipping {input_path}: no active elements")
        return

    bg_color = data.get("appState", {}).get("viewBackgroundColor", "#ffffff")

    min_x, min_y, max_x, max_y = compute_bounding_box(active)
    offset_x = min_x - PADDING
    offset_y = min_y - PADDING
    svg_w = (max_x - min_x) + 2 * PADDING
    svg_h = (max_y - min_y) + 2 * PADDING

    markers = {}
    svg_elements = []

    for el in active:
        rendered = render_element(el, offset_x, offset_y, markers)
        if rendered:
            svg_elements.append(rendered)

    defs_content = ""
    if markers:
        defs_content = "<defs>\n" + "\n".join(markers.values()) + "\n</defs>"

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
<rect width="100%" height="100%" fill="{bg_color}" />
{defs_content}
{chr(10).join(svg_elements)}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Created {output_path}")


def main():
    for src, dst in FILES:
        input_path = os.path.join(DIAGRAM_DIR, src)
        output_path = os.path.join(DIAGRAM_DIR, dst)
        if not os.path.exists(input_path):
            print(f"  Missing: {input_path}")
            continue
        print(f"Converting {src} -> {dst}")
        convert_file(input_path, output_path)
    print("Done.")


if __name__ == "__main__":
    main()
