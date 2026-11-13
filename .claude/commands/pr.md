---
description: Push the current branch and open a pull request filled in from the PR template
allowed-tools: Bash(git status*), Bash(git log*), Bash(git diff*), Bash(git branch --show-current), Bash(git push -u origin HEAD), Bash(gh pr create *), Bash(gh pr view *), Bash(gh auth status*), Bash(python -m unittest*), Bash(python scripts/check_translations.py), Bash(mkdocs build*), Read, Grep, Glob
---

Open a pull request for the current branch, with a description that follows `.github/pull_request_template.md`.

Extra notes from the user (may be empty): $ARGUMENTS

## Steps

1. **Check the branch.** Run `git status` and `git branch --show-current`. Stop and tell the user if:
   - the current branch is `main`,
   - there are uncommitted changes (ask whether to commit them first),
   - the branch has no commits ahead of `origin/main` (`git log origin/main..HEAD --oneline` is empty).

2. **Collect the changes.** Read `git log origin/main..HEAD` (full messages) and `git diff origin/main...HEAD --stat`. Read the diff of files when the commit messages do not explain a change well enough.

3. **Run the checks** and keep their results:
   - `python -m unittest discover -s tests`
   - `python scripts/check_translations.py`
   - `mkdocs build --strict` (build into a temporary directory, not `site/`)

4. **Fill in the template.** Read `.github/pull_request_template.md` and keep its exact headings and checklist items, in English.
   - **Summary**: two to four sentences on what changed and why.
   - **Type of change**: tick every type that applies.
   - Add a **Changes** section after Type of change with a short bullet list grouped by area.
   - **Checklist**: tick an item only when it is verified. Tick the two check commands only if they passed in step 3. Tick "Checked in light and dark mode, and at phone width" only if the user said so or it was verified in this session; otherwise leave it unticked and mention it. Items that do not apply (e.g. no new pages) are ticked and marked `(n/a)`.
   - **Screenshots**: remove the section unless there are visual changes; for visual changes leave the placeholder and remind the user to add screenshots.
   - End the description with the attribution line required by the session instructions, if any.

5. **Title.** Short, imperative, in English, max ~70 characters, summarising the whole branch.

6. **Push and create.**
   - `git push -u origin HEAD` (pushes the current branch; step 1 already stopped on `main`)
   - Write the description to a temporary file and run `gh pr create --base main --title "<title>" --body-file <file>`.
   - If `gh` is not installed or not logged in (`gh auth status` fails), do not push. Print the title and the full description in a code block, plus the link `https://github.com/Finito21/Cybersecurity/compare/main...<branch>?expand=1`, and tell the user to run `gh auth login`.

7. **Report** the PR URL, which checklist items are left unticked and why, and remind the user that the `Checks` workflow will run on the PR.

If any check in step 3 fails, do not create the PR. Show the failure and ask the user how to proceed.
