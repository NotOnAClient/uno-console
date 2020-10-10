# uno-console
Console/text based online multiplayer Uno game written with Python.

# How to use
Using this app is self explanatory. Enter the number of the card that you want to play.

# Build
You can build the client using `Pyinstaller` using this command:
```
pyinstaller --onedir client.py
```
You could also use: 
```
pyinstaller --onefile client.py
```
(slower, but you only get the .exe file and nothing else)

# Note
1. Make sure that `client_settings.txt` is in the same directory as the client script or else it will not work.
2. A player disconnecting from the server may cause the server to crash.
