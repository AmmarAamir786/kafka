Get the docker image
docker pull apache/kafka:3.7.0

Start the kafka docker container
docker run -d --name mykafka -p 9092:9092 apache/kafka:3.7.0
(use -d if you wanna use it in bg)

Check to see if container running:
docker ps

Copy the container name, and give the following command to attach:
docker exec -it <container-name> /bin/bash
replace <container-name> with mykafka
We do this so we get inside the consider and perfrom operations

Note: Kafka commands are in this directory in the container
Alll the existing scripts are in this directory
kafka topics are also in this directory
cd /opt/kafka/bin

CREATE A TOPIC TO STORE YOUR EVENTS
/opt/kafka/bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
#/opt/kafka/bin/kafka-topics.sh: absolute path
#--create --topic quickstart-events = create topic with the name "quickstart-events"
#--bootstrap-server localhost:9092 = location where we want to create our topic

Describe the topic
/opt/kafka/bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
#the data will be stored inside the partition which inside the topic

WRITE SOME EVENTS INTO THE TOPIC AS A PRODUCER
/opt/kafka/bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
You can stop the producer client with Ctrl-C at any time.

Open a new window and make it a consumer
docker exec -it <container-name> /bin/bash
/opt/kafka/bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
You can stop the consumer client with Ctrl-C at any time.


close the container by:
docker stop mykafka

Kafka UI (ignore for now)

#create a network seperate for the ui
docker network create -d bridge kafka-net

#-d here means what type of driver we need
#bridge = multiple networks can be connected
#kafka-net = name we set

check if it is working
docker network ls

run the network with our kafka container
docker run -p 9092:9092 --network kafka-net --name mykafka apache/kafka:3.7.0

open new terminal
docker run -it -p 8080:8080 --network kafka-net -e DYNAMIC_CONFIG_ENABLED=true provectuslabs/kafka-ui
#goto http://localhost:8080/ to see ifts working
