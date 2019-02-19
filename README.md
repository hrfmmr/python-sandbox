## Set up

```
$ make setup
```

## Run Daemons

```
# run daemons
$ pipenv run daemonize run-daemons 3

# check daemons
$ find ./daemons -name "*.log" | xargs tail -f

# clean daemons
$ make clean
```
