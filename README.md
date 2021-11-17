# alphabot

RaspServer: server, scritto in python3 con socket TCP, da caricare nel raspberry pi, in grado di ricevere messaggi( corrispondenti ai movimenti complessi) dal raspClinet  ed eseguirli

RaspClient: client, scritto in python3 con socket TCP, da connettere al raspServer, in grado di mandare messaggi ( corrispondenti ai movimenti complessi) al raspServer, che li andrà ad eseguire

alfabot.db: database contenente i movimenti complessi e le sequenza di movimenti semplici che li compongono

### Movimenti
nella tabella seguente vengono riportati i movimenti composti che possono essere eseguiti dall'alfabot

## Movimenti composti
| Nome comando      | Descrizione                        | 
| :-------- | :--------------------------------- | 
| `ESSE`  | Questo comando consente di far muovere l'Alphabot nella maniera tale da percorrere una S immaginaria   |
| `TRIANGOLO`  | Questo comando consente di far muovere l'Alphabot nella maniera tale da creare un triangolo immaginario    | 
| `QUADRATO`  | Questo comando consente di far muovere l'Alphabot nella maniera tale da creare un quadrato immaginario  |

