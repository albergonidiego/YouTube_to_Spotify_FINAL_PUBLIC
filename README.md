# YouTube_to_Spotify_FINAL_PUBLIC
This is a little project I went through to learn Python.
It was inspired by: The Come Up -> https://www.youtube.com/watch?v=7J_qcttfnJA
I've enhanced the scope to cover more options and to experiment with other Python libraries

Small application allowing the user to create Spotify playlists starting from YouTube content. Includes a simple GUI to navigate through the options (disclaimer: the GUI is functional but does not properly handle all the edge cases, meaning that it may get stuck).
All the necessary libraries are listed within the files, I've installed them manually in PyCharm.

Before you are able to run the code you must follow some initial steps:
1. In the prova.py file, at row 72 you must provide your YouTube channel ID. As it turns out, YouTube only allows you to create Playlists if you have a channel.
2. You have to provide your YouTube API v3 project details and OAuth credentials (client_id.json)
3. You have to provide your Spotify details (secrets.py).
Details on how to obtain all the info are within the files
