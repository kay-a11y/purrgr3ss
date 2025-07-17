import difflib

def inject_tags(text: str, tags: dict) -> str:
    """
    Replace all placeholders in the text with corresponding tag values.

    Example:
        inject_tags("Today is {{DATE_TODAY}}", {"{{DATE_TODAY}}": "2025-07-17"})
    """
    for k, v in tags.items():
        text = text.replace(k, v)
    return text

def replace_anchored_blocks(lines: list[str], anchors: dict) -> list[str]:
    """
    Given a list of lines and a dict of HTML anchors (e.g. 'DATE-TODAY': '<sub>...</sub>'),
    replaces the line immediately following each <!--DATE-XYZ--> marker with the new content.
    """
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("<!--DATE-"):
            # from <!--DATE-TODAY-->, get just: 'DATE-TODAY'
            anchor_key = line.strip().strip("<!-->").strip()
            if anchor_key in anchors:
                output.append(line)  # keep the comment line
                i += 1  # ← move to next line (expected: <sub>)
                if i < len(lines) and lines[i].strip().startswith("<sub>"):
                    i += 1  # ← move *past* the <sub>, don't add it to output
                output.append(anchors[anchor_key] + "\n")  # add new date line
                continue
        output.append(line)
        i += 1
    return output

def diff_preview(original_lines: list[str], updated_lines: list[str], fromfile="original", tofile="updated") -> str:
    """
    Return a unified diff preview between the original and updated file contents.
    """
    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile=fromfile,
        tofile=tofile,
        lineterm=''
    )
    return '\n'.join(diff)

if __name__ == "__main__":
    print(inject_tags("Today is {{DATE_TODAY}}", {"{{DATE_TODAY}}": "2025-07-17"}))