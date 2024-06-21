command to permanently remove some files from a repo and its history:

```
git filter-branch --force --index-filter   'git rm -r --cached --ignore-unmatch ./data/processed/transcriptions_txt'   --prune-empty --tag-name-filter cat -- --all
```

must be executed from the top of the repo

- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- https://stackoverflow.com/questions/2004024/how-to-permanently-delete-a-file-stored-in-git