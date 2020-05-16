# Tute
Un Juego De Tute Para Jugar Con La Familia

Run install-win to install on windows or install to install on mac (not yet up and running.)

For the future I might consider running this in a virtual environment or something but not yet.

For me the goal of the game is as such (i.e. what I'm learning): it will be a game of tute that:
* A server using sockets exists that will run the game in real time for users that are running clients
* Clients have a gui where you can click on a card to play it and so on
* It can be played from two to four players and a server where the server is on a different network from the users
* All packets sent to and from are encrypted so that the game is secure (and I practice this)

To make the second point work I intend to have it so that you can click to select a card and then click to move it to another spot. The cards will be alligned left to right for you on the bottom and you will see some card backs for the other players going in a circle. To keep it simple I'll have it display first on the left, then in front, then in a circle around a square table. Cards that are down you can see on the middle of the table.

To make clicking easier I have to consider whether to make this full screen and hard-code screen positions or do relative positions. I'd highly prefer relative positions if this is possible.

To make the third point I need to make a port forward script from the router. I intend to use this primarily on my Pi so I'll try to write a script if possible for automatic UPnP or something along those lines. If that's not possible then Ill just hard-code it for myself and to think about security I'll have to think about what I publish to github.