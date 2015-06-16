# WebSocket Breadboard

A simple extendable websocket listener to get you started building multiplayer HTML5 browser games.

> Check out the [example games](https://github.com/plefferts/ws-breadboard-examples).

###Great for experiments, side-projects, learning to code.

- code your front-end in HTML5 and javascript
- build the back-end from pre-written plugins, or code your own (in python)
- distribute your game as a `.exe` or `.app` (for Windows or Mac)
- players host their own server (like minecraft's `Open to LAN`)

###Light-weight, super simple
- start coding right away
- no server bills
- write your complex MMO back-end later

##How it works
1. Download and run the server app to host a LAN game.
  - The app runs a local webserver to host your game code right from disk.
2. Click the link to play the game in the browser.
  - Your browser loads the game's HTML and javascript
  - Your javascript opens a websocket connection to the server for real-time updates
3. Send the link to other players so they can join your game.
  - Their browsers load the game the same way you did.
  - Each player's browser sends messages to the server through the websocket.

##Technical Details
- written in Python
- based on `asynchat`
- executables built with `py2app` and `py2exe`


#Writing Plugins
coming soon

