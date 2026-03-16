# Git ORIGINS

## View current remotes

```bash
git remote -v
```

## Add a remote origin

```bash
git remote add origin <url>
```

## Change (overwrite) existing origin URL

```bash
git remote set-url origin <new-url>
```

## Rename a remote

```bash
git remote rename origin <new-name>
```

## Delete a remote

```bash
git remote remove origin
```

## Add a second remote (e.g. upstream)

```bash
git remote add upstream <url>
```

## Push to a specific remote

```bash
git push origin main
git push upstream main
```

## Set default upstream tracking branch

```bash
git push -u origin main
```

## Fetch from a specific remote

```bash
git fetch origin
git fetch upstream
```

## Pull from a specific remote

```bash
git pull origin main
git pull upstream main
```
