from ingest.chunking import chunk_filing, extract_filing_text, parse_filing

FILING_METADATA = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "form": "10-K",
    "fiscal_year": 2025,
    "filing_date": "2025-10-31",
    "accession_number": "0000320193-25-000001",
}

HTML = """
<html><body>
<p>Item 1. Business</p>
<p>""" + ("Apple designs and sells consumer electronics. " * 40) + """</p>
<p>Item 1A. Risk Factors</p>
<p>""" + ("The Company faces competition in many markets. " * 40) + """</p>
<table>
  <tr><td>Year</td><td>Revenue</td></tr>
  <tr><td>2024</td><td>$391,035</td></tr>
  <tr><td>2025</td><td>$416,161</td></tr>
</table>
<p>Item 7. Management's Discussion and Analysis</p>
<p>Services revenue reached a new all-time high.</p>
</body></html>
"""


def test_parse_filing_marks_tables_in_order():
    text, tables = parse_filing(HTML)
    assert "[[TABLE:0]]" in text
    assert len(tables) == 1
    assert tables[0].headers == ("Year", "Revenue")
    assert len(tables[0].rows) == 2


def test_chunk_filing_tracks_sections_and_tables():
    records = chunk_filing(HTML, FILING_METADATA)
    assert records, "expected at least one chunk"

    narrative = [r for r in records if r.chunk_metadata["chunk_kind"] == "narrative"]
    table_rows = [r for r in records if r.chunk_metadata["chunk_kind"] == "table_row"]
    assert narrative and table_rows

    sections = {r.section for r in narrative}
    assert any(s and s.startswith("Item 1") for s in sections)
    assert any(s and s.startswith("Item 7") for s in sections)

    for record in table_rows:
        assert record.chunk_metadata["table"]["markdown"].startswith("| Year | Revenue |")

    indexes = [r.chunk_index for r in records]
    assert indexes == list(range(len(records)))


def test_extract_filing_text_replaces_tables_with_marker():
    text = extract_filing_text(HTML)
    assert "[table]" in text
    assert "[[TABLE:" not in text
