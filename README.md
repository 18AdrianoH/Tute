# Tute
Un Juego De Tute Para Jugar Con La Familia

Run install-win to install on windows or install to install on mac (not yet up and running.)

For the future I might consider running this in a virtual environment or something but not yet.

For me the goal of the game is as such (i.e. what I'm learning): it will be a game of tute that:
* A server using sockets exists that will run the game in real time for users that are running clients
* Clients have a gui where you can click on a card to play it and so on
* It can be played from two to four players and a server where the server is on a different network from the users
* All packets sent to and from are encrypted so that the game is secure (and I practice this)
* Checkpoint game-states to a file in case of a crash (i.e. save/load games)

To make the second point work I intend to have it so that you can click to select a card and then click to move it to another spot. The cards will be alligned left to right for you on the bottom and you will see some card backs for the other players going in a circle. To keep it simple I'll have it display first on the left, then in front, then in a circle around a square table. Cards that are down you can see on the middle of the table.

To make clicking easier I have to consider whether to make this full screen and hard-code screen positions or do relative positions. I'd highly prefer relative positions if this is possible.

To make the third point I need to make a port forward script from the router. I intend to use this primarily on my Pi so I'll try to write a script if possible for automatic UPnP or something along those lines. If that's not possible then Ill just hard-code it for myself and to think about security I'll have to think about what I publish to github.

## Notes As Of May 16, 2020
I will simplify this process by making it a hard-coded port-forward and by additionally making it so that it only supports
four players.

The way the game works is the middle has three cards from left to right in three spots. Each player will have the max cards possible such that everyone has equal cards (note that this should be 12 for four players). A random suit is picked before each round. We will proceed for three games which each consists of many rounds.

I also want it to be possible to put settings for some basic rule changes in a file that you can edit.

## Update As of May 17, 2020
I'm probably going to host this on the cloud. A tutorial I sort of followed at "https://www.youtube.com/watch?v=KQasIwElg3w&list=PLzMcBGfZo4-kR7Rh-7JCVDN8lm3Utumvq&index=10" used linude and gave us some free credits potentially so I might just use linude, but AWS is also an option.

## Update As of June 5th 2020
Started working on this last night again for the first time since May 17. I am scrapping the elegant OOP of structs for now. I will make an implementation with barely any OOP, no security for sockets, and no thread safety in the code. Once I get this to work with a nice sequential game I'll add all of those things later if I feel so compelled. I just want to be able to play with Delia once So Things to fix later:

1. finish adding proper oop (make classes for player, etc.... that are actually used, pickle)
2. add checks for errors where people make mistakes (try catch and just more ifs)
3. add thread safety (locks)
4. add openSSL for some sort of RSA or diffie helman for secure transmission (openSSL or quic etc...)
5. add support for more/less than 4 players
6. add more responsivity to controls and instead of using keys control actions with mouse