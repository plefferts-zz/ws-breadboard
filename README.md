# WebSocket Breadboard

A simple extendable websocket listener to get you started building multiplayer HTML5 browser games.

- Light-weight, super simple
- Great for experiments, side-projects, learning to code.

> Check out the [example games](https://github.com/plefferts/ws-breadboard-examples).

###What you do
- Code your front-end in HTML5 and javascript
- Build the back-end from pre-written plugins, or code your own (in python)
- Start coding right away
- Write your complex MMO back-end later

###What you get
- Ability to distribute your beta multiplayer game as a `.exe` or `.app` (for Windows or Mac)
- Players host their own servers (like minecraft's `Open to LAN`)
- No server bills

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

#Contributing

##Build
    python3 setup.py py2app
