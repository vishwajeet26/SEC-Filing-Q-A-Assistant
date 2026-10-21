from ingest.sec_tables import extract_sec_tables


def test_extracts_simple_table():
    html = """
    <div>
      <p>Consolidated Statements of Operations (in millions)</p>
      <table>
        <tr><th>Year</th><th>Net income</th></tr>
        <tr><td>2024</td><td>$93,736</td></tr>
        <tr><td>2025</td><td>$112,010</td></tr>
      </table>
    </div>
    """
    tables = extract_sec_tables(html)
    assert len(tables) == 1
    table = tables[0]
    assert table.headers == ("Year", "Net income")
    assert len(table.rows) == 2
    assert table.rows[0].cells == ("2024", "$93,736")
    assert "in millions" in (table.units or "").lower()
    assert "Consolidated Statements" in (table.title or "")


def test_skips_mostly_empty_layout_table():
    html = """
    <table>
      <tr><td></td><td></td><td></td></tr>
      <tr><td>x</td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
      <tr><td></td><td></td><td></td></tr>
    </table>
    """
    assert extract_sec_tables(html) == []


def test_markdown_renders_rows():
    html = """
    <table>
      <tr><th>A</th><th>B</th></tr>
      <tr><td>1</td><td>2</td></tr>
    </table>
    """
    (table,) = extract_sec_tables(html)
    assert table.markdown == "| A | B |\n|---|---|\n| 1 | 2 |"
