# Git TAGS

## Delete all local tags

git tag -l | ForEach-Object { git tag -d $_ }

## Delete all remote tags

git tag -l | ForEach-Object { git push --delete origin $_ }

git push --delete origin v1.1.0-FINAL-13JAN2026
git push --delete origin v2.0.0-16JAN2026

## List all remote tags

git ls-remote --tags origin

## Delete locally first
git tag -d <tag-name>

## Then delete from remote
git push origin --delete <tag-name>