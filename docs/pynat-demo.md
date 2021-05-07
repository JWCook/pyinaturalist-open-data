# Asciicast

For reference, commands to record an asciicast and convert to a gif:
```
pip install asciinema
docker pull asciinema/asciicast2gif

asciinema rec --title pynat-demo --overwrite docs/pynat-demo.cast
docker run --rm \
    -v $PWD/docs:/data \
    asciinema/asciicast2gif \
    -t monokai \
    -w 110 \
    pynat-demo.cast pynat-demo.gif
```
