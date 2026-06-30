\*\*Plan: Rename globex\_ to chroma\_\*\*



This will be a controlled refactor: snapshot the repo first, then rename the implementation surface in lockstep with tests, configs, and docs, and finish with a test gate plus a workspace-wide search to catch anything missed. There does not appear to be an existing CI workflow in this repo, so the local `pytest` run becomes the effective gate unless you want a new workflow added as part of the change.



\*\*Steps\*\*

1\. Create a rollback point before editing anything. Use git history as the recovery anchor and, if desired, add a branch/tag snapshot so the pre-rename state is easy to return to.

2\. Rename the Python code surface in globex\_service.py and globex\_utils.py. This includes file names, imports, class/function names, logger names, and any default prefix values so the code stays internally consistent.

3\. Update the CLI layer in globex\_cli.py and globex\_refactor.py. The refactor helper currently searches for the old prefix, so it needs to align with the new naming or be generalized for the post-rename state.

4\. Update the tests in test\_globex\_service.py and test\_globex\_utils.py so imports, method calls, and assertions reflect the renamed API.

5\. Update config and docs in globex\_settings.yaml, globex\_logging.yaml, globex\_overview.md, globex\_architecture.md, globex\_api.md, and README.md so user-facing references and YAML keys follow the new prefix where that is part of the demo identity.

6\. Run the validation gate after the rename. Because there is no visible CI definition in the repo today, the gate is local `pytest`; if validation fails, repair the renamed slice before expanding scope.

7\. Do a final workspace search for `globex\_` to confirm only intentional leftovers remain, such as historical wording or the backup snapshot.



\*\*Relevant files\*\*

\- globex\_service.py and globex\_utils.py for the main implementation rename.

\- globex\_cli.py and globex\_refactor.py for command entry points and the bulk-rename helper.

\- test\_globex\_service.py and test\_globex\_utils.py for import and behavior updates.

\- globex\_settings.yaml and globex\_logging.yaml for prefix-bearing config keys.

\- globex\_overview.md, globex\_architecture.md, globex\_api.md, and README.md for branding and instructions.



\*\*Verification\*\*

1\. Run `pytest` from the repo root and require a clean pass.

2\. Search the workspace for `globex\_` after the edits and inspect any remaining matches.

3\. Review the diff for dangling imports, module names, or logger/config references that would break runtime behavior.



\*\*Decisions\*\*

\- The plan assumes a full rename of code-meaningful `globex\_` prefixes to `chroma\_`, not just file names.

\- Docs and README should be updated where the old naming is part of the demo identity.

\- Rollback should rely on git history plus a pre-edit snapshot.

\- No unrelated packaging or dependency work is included.



\*\*Further Considerations\*\*

1\. Do you want only prefix renames, or should all human-readable Globex branding in docs/comments also become Chroma?

2\. Should the rollback backup be a git branch/tag only, or do you want a separate file-level backup before the refactor starts?

3\. If you want CI enforcement beyond local testing, the next step would be adding a lightweight workflow that runs `pytest` on push and pull request.





