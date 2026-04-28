# Rummy

National Recording Rummy is an implementation of the game of gin rummy (specifically the rules known to the family of its creator) running on the (unrelated) National Recording Registry website.

## Running it

Frontend is a Svelte app, run with `npm run dev` (and bundled with `npm run build` to run on the static site, nationalrecordingregistry.net); backend is a Flask app which can be run locally with `flask run` when in the backend folder (or `flask --app backend/app run`) when not; a `wsgi.py` exists to run it on the distant server.

