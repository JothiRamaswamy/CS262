## High Level Design
Each machine is fundamentally represented as a process and corresponding machines communicate with each other through a client-server architecture. 

## Design Decisions
We can think of each machine as having a client and a server. The client of one machine is connected to the server of another machine, creating a triangular commmuncication path. For example, the client of machine 0 is connected to the server of machine 1; the client of machine 1 is connected to the server of machine 2, and the client of machine 2 is connected to the server of machine 0. Thus, we are able to specify recipients/senders based on whether we use the client or the server.

We understand that this is not robustly scalable beyond three machines, but thought this was the cleanest deisgn for a simple three machine communciation protocol.

## Analysis of Logical Clock Time
In the normal case (the case according to the assignment specification), the jumps are according to our intuition. The machine with the highest clock rate has near no jumps, and if we plot local logical clock time against global system time, the relationship is almost perfectly linear. The machines with the second and third highest clock times experience more jumps with the lower clock rates experiencing larger jumps. This intuitively makes sense because the faster machines are able to send messages more quickly than the slower ones, so the slower ones will have to read the messages before sending, but as they do so slowly, the faster machines keep sending messages and the messages keep piling up in the queue.

## Analysis of Queue size

For the above reason, it also makes sense that the faster clocks tend to have a queue size close to 0, while the slower clocks tend to see an increase in the queue size over time. The machines with a middle level of speed are a mix in the middle, and tend to see queue sizes closer to 0, but still retrieve messages more often than the faster machines.

## Analysis of Event Distribution

Also for similar reasons mentioned above, there was a discrepancy between the types of events performed (send message, retrive message, internal event) based on the machine speed. The fastest machines tended to have more send message events and internal events than retrieve message events because it was more likely to have an empty message queue. The slower machines tended to only really have retrieve message events because their queue was more likely to contain messages. The machines with a middle level of speed tended to lie somewhere in the middle.

## Analysis of Logical Clock Drift

Similar to the analysis of the logical clock jump size, the logical clock drift from the system clock tended to be larger over time in the slower machines than the faster machines. Since the fastest machines tended to have constant 1-1 logical clock time increases with each action, there was close to zero drift amongst these machines. For the slower machines, since they had larger logical clock jumps, and more jumps on average, they also tended to have a larger drift from the system time over the course of the minute that we ran the algorithm.

## Analysis of Changes in the Clock Rate Range

We tested out our code with additional clock rate ranges of: [1,1], [1,4], [1,8], [1,10]. If we shrink the clock rate, we see that the average jump sizes of the second and third highest clock rate machines also decrease, and that there are less of them overall. This is just simple statistics, where the order statistics of the uniform in a shrunk range are also themselves shrunk; thus, resulting in a system where the clock rates are all closer and resulting in less jumps. This also demonstrates that the drift in the logical clock time compared to the system time is much lower when shrinking the clock rate.

We also see that shrinking the clock rate range results in a more even distribution of send message events/internal events and receive events across machines of all speeds. This is due to the decrease in the speed discrepancy of the machines, so one machine is less liekly to dominate by sending machines relatively much faster than the other machines. This also means that the queue size across these machines is lower on average, and closer to 0. 

On the other hand, with a larger clock rate range, we see much more discrepancy between the clock rates of the different machines, resulting in larger logical clock jumps, drift, and queue sizes for the slowest machines, and resulting in a larger proportion of events on the slower machines being retrieve message events.

## Analysis of the change in Internal Event Likelihood
We tested our code with task ranges of [1,3], [1,5], [1,7], [1,20], where any task number above 3 is an internal event. If we decrease the likelihood of an internal event, we see that the discrepancy between event types on each machine increase. Spefically, the slower machines have a larger proportion of receiving messages and the faster machines have a larger proportion of sending messages. This makes sense because the faster machines are more likely to send a message now when their machines have no messages to read, so they send more messages as a result.

One thing that surprised me was that the size of the logical clock jumps were smaller, even though more messages were being sent/received. This might be because the internal events that separated message sends could have caused the discrepancy between the logical clock time of one send and the following send to be larger than it would be without the internal events. As a result, without these internal events, the logical clock times between the send message events are closer together, resulting in smaller logical clock jumps on the receiving machine.
