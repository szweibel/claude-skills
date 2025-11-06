# WorldCat Metadata API

The Metadata API provides detailed bibliographic records and metadata for library materials.

## Python Library: bookops-worldcat

The recommended way to interact with the Metadata API is through the `bookops-worldcat` Python library.

**Installation:**
```bash
pip install bookops-worldcat
```

**Documentation:** https://bookops-cat.github.io/bookops-worldcat/

## Authentication

```python
from bookops_worldcat import MetadataSession, WorldcatAccessToken

# Get access token
token = WorldcatAccessToken(
    key=OCLC_CLIENT_ID,
    secret=OCLC_CLIENT_SECRET,
    scopes="WorldCatMetadataAPI"
)

# Create session
session = MetadataSession(authorization=token)
```

## Key Methods

### brief_bibs_search()

Search for bibliographic records.

```python
response = session.brief_bibs_search(q="title:Moby Dick")
```

**Parameters:**
- `q`: Query string using WorldCat query syntax
- Additional filters available (see official docs)

**Returns:** JSON response with brief bibliographic records

### brief_bibs_get()

Get a single record by OCLC number.

```python
response = session.brief_bibs_get(oclcNumber="123456")
```

**Parameters:**
- `oclcNumber`: The OCLC control number

**Returns:** Detailed bibliographic record

### bib_get_classification()

Get LC/Dewey classification for a record.

```python
response = session.bib_get_classification(oclcNumber="123456")
```

**Returns:** Classification data (LC call number, Dewey decimal, etc.)

### summary_holdings_search()

Check holdings at specific institutions.

```python
response = session.summary_holdings_search(
    oclcNumber="123456",
    heldBySymbol=["ZGM", "NYP"]  # Check specific libraries
)
```

**Parameters:**
- `oclcNumber`: OCLC number to check
- `heldBySymbol`: List of institution symbols to check

**Returns:** Holdings information for specified institutions

**Note:** This checks specific institutions only. For ALL holdings, use the Search API V2 (see search-api-v2.md).

## Query Syntax

WorldCat uses a specific query syntax:

**Examples:**
```python
# Title search
q="title:Moby Dick"

# Author search
q="author:Melville Herman"

# ISBN search
q="isbn:9780140283334"

# Combined search
q="title:Moby Dick AND author:Melville"

# Year filter
q="title:Pound AND year:1999"
```

**Common fields:**
- `title:` - Title keyword search
- `author:` - Author name
- `isbn:` - ISBN (10 or 13 digit)
- `issn:` - ISSN
- `year:` - Publication year
- `publisher:` - Publisher name
- `subject:` - Subject headings

## Best Practices

### Progressive Search Strategy

When searching with incomplete or messy citations:

1. **Start broad** - Use title keywords only
2. **Add filters progressively** if too many results
3. **Pick best match** based on metadata alignment

**Example:**
```python
# Bad: Too specific, may return 0 results
q = "Ezra and Dorothy Pound: Letters in Captivity, 1945–1946"

# Good: Broad initial search
q = "title:Pound Letters Captivity"
# If 50+ results, add year filter:
q = "title:Pound Letters Captivity AND year:1999"
# Then manually filter by publisher/author from results
```

**Why:** Bibliographic data has variations (punctuation, encoding, formatting). Better to get 20 results and filter than 0 results from being too specific.

### Handling Encoding Issues

Look for common encoding problems:
- `?` or `�` characters (garbled text)
- Example: "Antigüedad" → "Antig?edad"

**Strategy:**
- Remove accents initially
- Add them back if no results found

### Working with Multiple Records

The same work may have multiple OCLC records:
- Print edition vs digital edition
- Different publishers
- Different languages

When relevant, check multiple records and document which was used.

## Common Workflows

### Find and Identify Items

```python
# 1. Search by ISBN (most reliable)
response = session.brief_bibs_search(q="isbn:9780140283334")

# 2. If no ISBN, use progressive keyword search
response = session.brief_bibs_search(q="title:Moby Dick")

# 3. Extract OCLC number from best match
oclc_number = response['briefRecords'][0]['oclcNumber']
```

### Get Complete Metadata

```python
# Get full record
record = session.brief_bibs_get(oclcNumber="123456")

# Extract metadata
title = record['title']
author = record['creator']
publisher = record['publisher']
isbn = record['isbns'][0] if 'isbns' in record else None
```

### Check Holdings at Specific Libraries

```python
# Check if specific libraries have this item
holdings = session.summary_holdings_search(
    oclcNumber="123456",
    heldBySymbol=["DLC", "NYP", "ZGM", "ZCU"]
)

# Extract which libraries have it
libraries_with_item = [
    h['oclcSymbol'] for h in holdings.get('briefHoldings', [])
]
```

## Error Handling

```python
try:
    response = session.brief_bibs_search(q="title:NonexistentBook")

    if not response.get('briefRecords'):
        print("No results found")
    else:
        # Process results
        pass

except Exception as e:
    print(f"API error: {e}")
```

## Rate Limits

The Metadata API has rate limits. The `bookops-worldcat` library handles token refresh automatically.

If you hit rate limits:
- Add delays between requests
- Use batch operations where available
- Cache results locally

## Official Documentation

- Metadata API Docs: https://www.oclc.org/developer/api/oclc-apis/worldcat-metadata-api.en.html
- bookops-worldcat Docs: https://bookops-cat.github.io/bookops-worldcat/
- OCLC Developer Network: https://developer.api.oclc.org/
