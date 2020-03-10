##Modification 1: records

At the moment the IBM application works as a trivial message board. In our case we want to implement anì non-modifiable database of the statistics of US flights. This is useful for insurance refunding.  Each flight must be described by the following fields:
```
    TRANSACTION ID: id of the transaction
    YEAR: year the flight took place
    DAY_OF_WEEK: 1..7, 1=Sunday
    FLIGHT_DATE: yyyymmaa
    OP_CARRIER_FL_NUM: flight number
    OP_CARRIER_AIRLINE_ID: unique id of the carrier line
    ORIGIN_AIRPORT_ID: unique id of the origin airport
    ORIGIN: origin airport name
    ORIGIN_CITY_NAME: origin city
    ORIGIN_STATE_NM: origin state
    DEST_AIRPORT_ID: unique id of the destination airport
    DEST: destination airport name
    DEST_CITY_NAME: destination city,
    DEST_STATE_NM: destination state
    DEP_TIME: local departure time
    DEP_DELAY: departure delay
    ARR_TIME: arrival time
    ARR_DELAY: arrival delay
    CANCELLED: 1=Yes, 0=No
    AIR_TIME: length of the flight
```
We want to design a blockchain whose transactions are records of the above described type.

##Modification 2: operations defined

The operations that must be allowed in the blockchain are:
 - add a new transactions
 - retrieve a transaction based on the transaction id
 - retrieve all the transactions of a block
    
##Modification 3: mining and storage

The mining operation must be invoked automatically every minute. In realty the mining process must be constantly carried on to make the chain more robust to attacks. However, for our purposes, this is possible only if you have a computer dedicated to the mining process. Blocks must contain at least one transaction (with the exception of the first block) and at most 1,000 transactions. Blocks must be stored in the disk as separate files. If you plan to have multiple miners in your implementation (this is optional) please pay attention that the joining phase must take into account the transfer of the entire chain. When the system is started, the blockchain must be recreated from the files: therefore, modifications must be persistent. 

##Modification 4: the application
The web application must allow the following operations:

 - Adding a new record to the chain
 - Query the status of a flight given OP_CARRIER_AIRLINE_ID and the DATE
 - Query the average delay of a flight carrier in a certain interval of time
 - Given a pair of cities A and B, and a time interval, count the number of flights connecting city A to city B


