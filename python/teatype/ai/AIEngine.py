# on first import, deploys, installs and launches the engine in the background (launches itself somehow)
# then, on subsequent imports, connects to the already running engine instance
# and provides a client interface to interact with it
# this way, the engine is only started once and can be reused across multiple scripts or sessions
# communicate via redis messages