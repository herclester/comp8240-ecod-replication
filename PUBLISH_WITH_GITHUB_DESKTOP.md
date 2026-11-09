# Publish using GitHub Desktop on Windows

The prepared folder is `comp8240-ecod-replication`, beside the original `pyod` folder. It contains a new local Git repository on branch `main`, with no commits and no remote. The original `pyod` repository and its origin remain untouched.

1. Open GitHub Desktop and sign in to the GitHub account where you want the project.
2. Choose **File > Add local repository**, then **Choose** and select the prepared `comp8240-ecod-replication` folder. Click **Add repository**. Do not select the old `pyod` folder.
3. Review the **Changes** list and compare it with `FILE_LIST.txt`. The README previews result figures and explains omitted data. No raw data, environment folder, private key, or original Git history should appear.
4. Enter `Initial COMP8240 ECOD replication` as the commit summary and click **Commit to main**. This creates your first local commit; it does not publish anything.
5. Click **Publish repository** to open its setup dialog. Confirm the name `comp8240-ecod-replication`, choose your personal account (rather than an unintended organisation), and add a description such as `COMP8240 partial ECOD replication, diagnostics, extensions, and explanation-faithfulness evaluation`.
6. To make the repository public, clear **Keep this code private**. Review the selected account and visibility. **Stop here until you are ready to publish.**
7. The final **Publish repository** button sends the repository to GitHub. This click is yours. After publishing, use **View on GitHub** and check that the README images and result links load. Copy the resulting repository URL into your report yourself.

There is no need to remove or change the original PyOD remote. This new local repository has no remote to remove. If the intended GitHub repository name already exists under your account, resolve that name conflict before publishing; do not overwrite an unrelated repository.

Official instructions:
- https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop
- https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop
