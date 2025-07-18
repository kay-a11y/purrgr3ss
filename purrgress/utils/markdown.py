import difflib

def inject_tags(text: str, tags: dict) -> str:
    for k, v in tags.items():
        text = text.replace(k, v)
    return text

def replace_anchored_blocks(lines: list[str], anchors: dict) -> list[str]:
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("<!--DATE-"):
            anchor_key = line.strip().strip("<!-->").strip()
            if anchor_key in anchors:
                output.append(line) 
                i += 1 
                if i < len(lines) and lines[i].strip().startswith("<sub>"):
                    i += 1 
                output.append(anchors[anchor_key] + "\n") 
                continue
        output.append(line)
        i += 1
    return output

def diff_preview(original_lines: list[str], updated_lines: list[str], fromfile="original", tofile="updated") -> str:
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