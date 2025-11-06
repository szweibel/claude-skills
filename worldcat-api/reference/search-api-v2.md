# WorldCat Search API V2

The Search API V2 provides comprehensive holdings data across ALL institutions worldwide. This is the preferred API for checking which libraries hold specific items.

**Key Difference from Metadata API:** The Search API V2 can return ALL institutions holding an item in a single API call, while the Metadata API requires checking institutions individually.

## Authentication

No Python library is available for Search API V2. Use direct REST calls with the `bookops-worldcat` token library.

```python
import requests
from bookops_worldcat import WorldcatAccessToken

# Get access token
token = WorldcatAccessToken(
    key=OCLC_CLIENT_ID,
    secret=OCLC_CLIENT_SECRET,
    scopes='wcapi:view_holdings wcapi:view_institution_holdings'
)
```

**Required Scopes:**
- `wcapi:view_holdings` - View holdings data
- `wcapi:view_institution_holdings` - View institution-level holdings

## Key Endpoint: Get ALL Holdings

**Endpoint:** `GET /worldcat/search/v2/bibs-holdings`

This endpoint returns ALL institutions holding an item in one API call.

```python
import requests
from bookops_worldcat import WorldcatAccessToken

# Authenticate
token = WorldcatAccessToken(
    key=OCLC_CLIENT_ID,
    secret=OCLC_CLIENT_SECRET,
    scopes='wcapi:view_holdings wcapi:view_institution_holdings'
)

# Get ALL institutions holding this item
url = 'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs-holdings'
headers = {
    'Authorization': f'Bearer {token.token_str}',
    'Accept': 'application/json'
}
params = {'oclcNumber': '123456'}

response = requests.get(url, headers=headers, params=params)
data = response.json()

# Extract institution symbols
institutions = []
for record in data.get('briefRecords', []):
    for holding in record.get('institutionHolding', {}).get('briefHoldings', []):
        institutions.append({
            'symbol': holding.get('oclcSymbol'),
            'name': holding.get('institutionName'),
            'country': holding.get('country')
        })

# Get just the symbols
symbols = [inst['symbol'] for inst in institutions]
# Returns: ["DLC", "NYP", "ZGM", "ZCU", ...]
```

## Why This Matters

**Inefficient approach (Metadata API - 150+ API calls):**
```python
# DON'T DO THIS
for code in institution_codes:  # BAD! 150 iterations
    check_if_institution_holds(oclc_number, code)
```

**Efficient approach (Search API V2 - 1 API call):**
```python
# DO THIS INSTEAD
# Get ALL holdings at once
holdings = get_all_holdings_via_search_api_v2(oclc_number)
symbols = set(holdings['institution_symbols'])

# Filter locally
tier_codes = {'NYP', 'ZCU', 'ZYU'}
matches = symbols & tier_codes
```

## Response Structure

**Example Response:**
```json
{
  "briefRecords": [
    {
      "oclcNumber": "123456",
      "title": "Example Book Title",
      "institutionHolding": {
        "totalHoldingCount": 243,
        "briefHoldings": [
          {
            "oclcSymbol": "DLC",
            "institutionName": "Library of Congress",
            "country": "US",
            "holdingSet": true
          },
          {
            "oclcSymbol": "NYP",
            "institutionName": "New York Public Library",
            "country": "US",
            "holdingSet": true
          }
          // ... many more institutions
        ]
      }
    }
  ]
}
```

## Institution Symbols

Common library symbols:

| Symbol | Institution |
|--------|-------------|
| DLC | Library of Congress |
| NYP | New York Public Library |
| ZGM | CUNY Graduate Center |
| ZCU | Columbia University |
| ZYU | Yale University |
| HUL | Harvard University |

Users typically maintain lists of institution symbols for their consortia.

## Common Workflows

### Get All Holdings for an Item

```python
def get_all_holdings(oclc_number):
    """Get all institutions holding an item."""
    url = 'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs-holdings'
    headers = {
        'Authorization': f'Bearer {token.token_str}',
        'Accept': 'application/json'
    }
    params = {'oclcNumber': oclc_number}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    institutions = []
    for record in data.get('briefRecords', []):
        holdings = record.get('institutionHolding', {}).get('briefHoldings', [])
        for holding in holdings:
            institutions.append({
                'symbol': holding.get('oclcSymbol'),
                'name': holding.get('institutionName'),
                'country': holding.get('country')
            })

    return institutions
```

### Filter by Institution List

```python
# Get all holdings
all_holdings = get_all_holdings("123456")
all_symbols = {h['symbol'] for h in all_holdings}

# Check against your institution list
my_institutions = {'NYP', 'ZCU', 'ZYU', 'HUL'}
matching_institutions = all_symbols & my_institutions

print(f"Held by {len(matching_institutions)} of our institutions")
print(f"Symbols: {matching_institutions}")
```

### Batch Processing with Holdings

```python
def process_items_with_holdings(oclc_numbers, institution_codes):
    """Process multiple items efficiently."""
    results = []

    for oclc_num in oclc_numbers:
        # Get all holdings for this item (1 API call)
        holdings = get_all_holdings(oclc_num)
        holding_symbols = {h['symbol'] for h in holdings}

        # Check locally (no API calls)
        matches = holding_symbols & institution_codes

        results.append({
            'oclc_number': oclc_num,
            'total_holdings': len(holdings),
            'matching_institutions': list(matches)
        })

    return results
```

## Error Handling

```python
import requests

def get_all_holdings_safe(oclc_number):
    """Get holdings with error handling."""
    url = 'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs-holdings'
    headers = {
        'Authorization': f'Bearer {token.token_str}',
        'Accept': 'application/json'
    }
    params = {'oclcNumber': oclc_number}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract holdings
        institutions = []
        for record in data.get('briefRecords', []):
            holdings = record.get('institutionHolding', {}).get('briefHoldings', [])
            for holding in holdings:
                institutions.append({
                    'symbol': holding.get('oclcSymbol'),
                    'name': holding.get('institutionName'),
                    'country': holding.get('country')
                })

        return institutions

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"OCLC number {oclc_number} not found")
            return []
        elif e.response.status_code == 401:
            print("Authentication failed - check credentials")
            return []
        else:
            raise
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return []
```

## Rate Limits

- The Search API V2 has rate limits
- Add delays between requests for batch processing
- Implement exponential backoff for retries

```python
import time

def get_holdings_with_retry(oclc_number, max_retries=3):
    """Get holdings with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return get_all_holdings(oclc_number)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception(f"Failed after {max_retries} retries")
```

## Regional Endpoints

The API has regional endpoints:

- **Americas:** `https://americas.discovery.api.oclc.org/`
- **Europe:** `https://europe.discovery.api.oclc.org/`
- **Asia-Pacific:** `https://asiapacific.discovery.api.oclc.org/`

Use the endpoint closest to your location for better performance.

## Performance Tips

1. **Cache results** - Holdings data doesn't change frequently
2. **Batch processing** - Process items in chunks with delays
3. **Filter locally** - Get all holdings once, filter in Python
4. **Use sets** - Set operations are faster than list comparisons
5. **Parallel requests** - Use `concurrent.futures` for multiple items (with rate limiting)

## Official Documentation

- Search API V2: https://developer.api.oclc.org/wcv2
- API Explorer: https://developer.api.oclc.org/wcv2#operations-tag-Bibs
- OCLC Developer Network: https://developer.api.oclc.org/
