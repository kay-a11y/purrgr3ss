def run(file, preview, write, tags_only, anchors_only):
    from purrgress.utils.path import path_to
    from purrgress.utils.date import date_vars, anchored_date_lines
    from purrgress.utils.markdown import inject_tags, replace_anchored_blocks, diff_preview

    md_path = path_to(*file.split("/"))

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if anchors_only:
        lines = content.splitlines(keepends=True)
    else:
        content = inject_tags(content, date_vars())
        lines = content.splitlines(keepends=True)

    if not tags_only:
        lines = replace_anchored_blocks(lines, anchored_date_lines())

    with open(md_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    if preview or not write:
        print("\n🧁 Preview of Changes:\n" + "-" * 40)
        print(diff_preview(original_lines, lines))
        if not write:
            print("\n💡 Use --write to apply changes.\n")
            return

    with open(md_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ File updated: {file}")
