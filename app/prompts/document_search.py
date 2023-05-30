document_search = """
INPUT: {input}

Based on the above input, please provide query terms to search with. Should be a simple search query. Return only the search terms in the fllowing format:

```
{{
    "search_terms": $SEARCH_TERMS
}}
```
"""
