# Development
This document explains how to set up a development environment to contribute to *archibus-automated-scheduler*.

## Background

To run the scheduler users are encouraged to fork the repository and uncomment the workflow.yml to enable the scheduled GitHub Actions workflow. The repository uses a composite action as:

```yml
justinj-evans/archibus-automated-scheduler@main
```
This composite action is referenced in the main [workflow.yml](.github\workflows\workflow.yml) file and checks out this code using 'actions/checkout@v4' into a 'composite-action-directory'. 

While this setup enables users to leverage the most recent release of the scheduler when they fork, the 'composite-action-directory' is necessary to avoid a path conflict when testing locally due to the simultaneous presence of main.py at the repository root. To avoid conflicts, local testing should explicitly reference the appropriate file path.

## Local Testing

Users can run [main.py](src\main.py) locally by uncommenting and simulating command-line arguments using sys.argv.

```python
# simulate command-line arguments for local testing
sys.argv = [ 'main.py',
              '--username', 'LASTFIRST',
              '--building_name', 'BUILDING',
              '--floor', 'ACRONYMNUMBER',    
              '--workstation', 'NUMBER',
              '--password', 'PASSWORD'
              ]
```

## Testing with GitHub Actions Locally
Since Selenium may behave differently in a local environment compared to GitHub Actions, it's recommended to test within a Docker-based environment. Use *[act](https://nektosact.com/)* to simulate GitHub Actions locally. *act* reads your workflows from the .github/workflows/ directory.

To configure local testing with act, follow these steps:

### Step 1: update [workflow.yml](.github\workflows\workflow.yml)
Change:
```yaml
      - name: Use Composite Action
        uses: justinj-evans/archibus-automated-scheduler@main 
        with:
          scheduling_args: ${{ secrets.ARCHIBUS_SCHEDULING_ARGS }}
```
To:
```yaml
      - name: Use Composite Action
        uses: ./
        with:
          scheduling_args: ${{ secrets.ARCHIBUS_SCHEDULING_ARGS }}
```
### Step 2: update [action.yml](action.yml)
From:
```yaml
  steps:
    - name: Checkout composite action repository code
      uses: actions/checkout@v4
      with:
        repository: justinj-evans/archibus-automated-scheduler
        clean: true
        path: composite-action-directory 
```
To:
```yaml
    - name: Checkout composite action repository code
      uses: ./composite-action-directory

```
### Step 3: run branch in Powershell
Replace <branch_name> and insert_here with your branch name and argument string, using:

```bash
act --job archibus-automated-scheduler -b insert_branch_name -s ARCHIBUS_SCHEDULING_ARGS="insert_here"
```
See an example secret in the main [README](README.md).

## Contribute

### Branch Naming
Branches will follow the naming scheme "type-number-summary". Ex: feature-2-click_action.
The accepted types for now are:
- feature
- doc
- bugfix

### Packaging and releasing
The release process is automated using GitHub Actions. Steps to trigger a release:

1. Create a tag for the desired release. Ensure the tag matches the SemVer format and is applied to the correct commit.
    ```
    git tag <MAJOR.MINOR.PATCH>
    ```

2. Push the tag to the remote repository:
    ```
    git push origin --tags
    ```

This process automatically starts the release workflow.