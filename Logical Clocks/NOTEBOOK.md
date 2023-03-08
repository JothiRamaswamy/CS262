## High Level Design
Each machine is fundamentally represented as a process and corresponding machines communicate with each other through a client-server architecture. 

## Design Decisions
We can think of each machine as having a client and a server. The client of one machine is connected to the server of another machine, creating a triangular commmuncication path. For example, the client of machine 0 is connected to the server of machine 1; the client of machine 1 is connected to the server of machine 2, and the client of machine 2 is connected to the server of machine 0. Thus, we are able to specify recipients/senders based on whether we use the client or the server.

We understand that this is not robustly scalable beyond three machines, but thought this was the cleanest deisgn for a simple three machine communciation protocol.
