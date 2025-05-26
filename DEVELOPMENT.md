# Development
This document explains how to set up a development environment to contribute to *archibus-automated-scheduler*.

## Background

To run the scheduler users are encouraged to fork the repository and uncomment the workflow.yml to initiate a regular Github Action scheduler. The repository uses a composite action 'justinj-evans/archibus-automated-scheduler@main' in the main workflow.yml file, and further checks out this code using 'actions/checkout@v4' into a 'composite-action-directory'. While this setup allows users to use the most up to date release of this data, it also forces the code to run out of a local path to not conflict with forked components (main.py in repo versus composite-action-directory/main.py).

## Local Testing

Users can run main.py locally by uncommenting and passing sys.argv.

```python
    # uncomment this out to run locally
    simulated args for testing
    sys.argv = [ 'main.py',
                 '--username', 'LASTFIRST',
                 '--building_name', 'BUILDING',
                 '--floor', 'ACRONYMNUMBER',    
                 '--workstation', 'NUMBER',
                 '--password', 'PASSWORD'
                 ]
```

## Test Github Action
It is recommended to test updates in Docker environment as selenium can behave different in local and in Github Action. To test Github Action locally use *[act](https://nektosact.com/)*, as it reads in your GitHub Actions from '.github/workflows/'.
  
The following steps are need to ensure [act] runs locally:

[1] update workflow.yml 
```
      - name: Use Composite Action
        uses: justinj-evans/archibus-automated-scheduler@main # use ./ for local dev.
        with:
          scheduling_args: ${{ secrets.ARCHIBUS_SCHEDULING_ARGS }}
```
to
```
      - name: Use Composite Action
        uses: ./
        with:
          scheduling_args: ${{ secrets.ARCHIBUS_SCHEDULING_ARGS }}
```
[2] update action.yml
```
  steps:
    - name: Checkout composite action repository code
      uses: actions/checkout@v4
      with:
        repository: justinj-evans/archibus-automated-scheduler
        clean: true
        path: composite-action-directory 
```
to
```
    - name: Checkout composite action repository code
      uses: ./composite-action-directory

```
[3] run branch in Powershell
```
act --job archibus-automated-scheduler -b insert_branch_name -s ARCHIBUS_SCHEDULING_ARGS="insert_here"
```
