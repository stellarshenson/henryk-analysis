command to permanently remove some files from a repo and its history:

```
git filter-branch --force --index-filter   'git rm -r --cached --ignore-unmatch ./data/processed/transcriptions_txt'   --prune-empty --tag-name-filter cat -- --all
```

must be executed from the top of the repo
