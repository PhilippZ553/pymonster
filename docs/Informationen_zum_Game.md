## Informationen zur Welt

| Parameter   | Wert  |
| ----------- | ----------- |
| Weltgröße | 71 x 34 |
| N | 3 |
| Startenergie| 10 |
|Energie/Field| 1|
|Grundumsatz | 1 |
|Teilungsenergie| 40 |
| Futter Energie | 5|

## Netzwerk

| Parameter      | Wert  |
| ----------- | ----------- |
| Server-IP | 127.0.0.1 |
| Server-Port| 9721|
| Hostname | arena.informatik.hs-augsburg.de |

## Kommunikation

1. **Initiale Nachricht nach der Anmeldung:**  
User ’gruppe01’ logged in successfully
2. **Format der Server-Nachrichten mit Biest-Informationen:**  
`ID#Energie#Umgebung`  
ID: Beast id (int)  
Energie: Energie des Beast (float)  
Umgebung: Das gesehene Spielfeld, also "N+1xN+1" (String)  
3. **Format der Befehle:**  
Server sendet: id, energy, Informationen des Feldes  
**Example:** "1#10#................................................."  
Client soll senden = f`"{beast_id} {MOVE}/{SPLIT} {d_x} {d_y}"`  
**Example:** "1 MOVE 1 0" (<= N-1)  
4. **Abmeldung**  
Forced by invalid move or command. 

## Commands des Servers und des Clients 

`"BEAST_COMMAND_REQUEST"` - Server erwartet Kommand des Client  
`"BEAST_GONE_INFO"` - Beast ist dead  
`"NO_BEASTS_LEFT_INFO"` - Kein Beast mehr, game over  
`"SHUTDOWN_INFO"` - Game ended  
`"MOVE"` - we move   
`"SPLIT"` - we split  

## Spielfeld

| String   | Information |
| ----------- | ----------- |
| . | leere Zelle |
| * | Futter |
| > | Biest größerer Energie |
| = | Biest gleicher Energie |
| < | Biest kleinerer Energie |

## Installation des Gruppen-Clients auf dem Server

1. Kopieren des Pakets auf den Server mit  
`scp PAKETPLACEHOLDERNAME.whl gruppe01@arena.informatik.hs-augsburg.de:/home/gruppe01`  
2. Anmelden auf dem Server im Terminal  
`ssh gruppe01@arena.informatik.hs-augsburg.de`  
3. Installation/Update des Pakets auf dem Server vom Terminal aus mit  
`pipx uninstall -y paket`  
`pipx install --system-site-packages ./paket.whl`  
4. **Einmalig**: Mit pipx installierte Software verfügbar machen mit  
`pipx ensurepath`