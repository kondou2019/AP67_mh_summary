def logseq_md_to_txt(lines: list[str]) -> list[str]:
    """!
    @brief logseqの.mdファイルを.txt形式に変更する
    先頭の"- "を削除する
    """
    lines0: list[str] = []
    for line in lines:
        # インデント
        tab_count = 0
        for c in line:
            if c == "\t":
                tab_count += 1
            else:
                break
        if tab_count != 0:
            line = line[tab_count:]
        #
        if line.startswith("- "):
            line = line[2:]
        lines0.append("\t" * tab_count + line)
    lines = lines0
    return lines
