# Datagen
Lots to be done still, run `./cli.py --help` for some instructions.

Always run `make` (i.e. type-checking and linting) before committing!

To run the standalone API, first run `./cli.py sim` and then in a second
terminal `./cli.py api`. The API endpoint displaying the most recent sensory
readings is at http://127.0.0.1:8080/readings.

You can edit the ./configs/datagen.yaml file as the simulation runs, just make
sure that your editor edits the file in-place. For vim, see [this
thread](https://github.com/gorakhargosh/watchdog/issues/56#issuecomment-1796587).
