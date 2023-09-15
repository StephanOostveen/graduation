#include "DataRouter.hpp"

Define_Module(DataRouter);

DataRouter::~DataRouter() noexcept {}

void DataRouter::initialize() {
	outputGateId   = gateBaseId("out");
	outputGateSize = gateSize("out");
}

/* Received a message from a node, broadcast it to all connected nodes
 * filtering on relevance should happen inside the connected nodes.
 * In order to avoid loopbacks we assume that the gateway tx/rx of a physical
 * have the same index into the in/out gate vector.
 */
void DataRouter::handleMessage(omnetpp::cMessage* msg) {
	for (int i = 0; i < outputGateSize; ++i) {
		if (msg->getArrivalGate()->getIndex() == i) {
			// Avoid loopback
			continue;
		}
		send(msg->dup(), outputGateId + i);
	}
	delete msg;
}