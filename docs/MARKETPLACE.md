# Marketplace release checklist

## Validate

```sh
claude plugin validate ./plugins/stillmirror-review --strict
claude plugin validate ./.claude-plugin/marketplace.json --strict
python3 -m unittest discover -s tests -v
```

## Smoke test local marketplace

From outside this repository:

```sh
claude plugin marketplace add /path/to/stillmirror-review --scope local
claude plugin install stillmirror-review@stillmirror --scope local
claude plugin details stillmirror-review
```

## Tag

```sh
claude plugin tag ./plugins/stillmirror-review --dry-run
claude plugin tag ./plugins/stillmirror-review --push
```

## Privacy check

```sh
rg -n "/Users/[[:alnum:]_-]+|Downloads|chat\\.html|Gemini|PRIVATE_PROMPT_TEXT|secret" \
  --glob '!docs/MARKETPLACE.md' \
  .claude-plugin plugins/stillmirror-review examples/stillmirror-review README.md docs
```

The check should produce no private data findings.
