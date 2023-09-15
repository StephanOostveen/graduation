#include "GatewayRunnable.hpp"
#include "omnetpp/cmessage.h"

#include <omnetpp.h>

Define_Module(GatewayRunnable);

GatewayRunnable::~GatewayRunnable() noexcept {}

void GatewayRunnable::handleMessage(omnetpp::cMessage* msg) {
	if (msg->isSelfMessage()) {
		Runnable::handleSelfMessage(msg);
		// Write tmp buffer to datadicts
	}

	// handle get response from data dict: delete msg and return

	// handle DataIn, store data in tmp buffer?
}