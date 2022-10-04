#include "Runnable.hpp"

#include <algorithm>
#include <array>
#include <cstdio>
#include <limits>
#include <string_view>

Define_Module(Runnable);

Runnable::~Runnable() noexcept {
	cancelAndDelete(invocationMsg);
}

void Runnable::initialize() {
	invocationMsg = new omnetpp::cMessage("Runnable");

	interfaceInputId        = gateBaseId("InterfaceInput$o");
	interfaceInputGateSize  = gateSize("InterfaceInput");
	interfaceOutputId       = gateBaseId("InterfaceOutput");
	interfaceOutputGateSize = gateSize("InterfaceOutput");

	scheduleAt(omnetpp::simTime(), invocationMsg);
}

void Runnable::handleMessage(omnetpp::cMessage* msg) {
	if (!msg->isSelfMessage()) {
		delete (msg);
		// msg is a get response from the data dict, nothing to do here
		return;
	}

	// self message should not be deleted, instead it is scheduled again at the end.
	using namespace std::literals::string_view_literals;
	static constexpr auto str             = "Invocation: "sv;
	static constexpr auto intBase10Digits = []() noexcept {
		int  length = 1;
		auto x      = std::numeric_limits<decltype(invocation)>::max();
		while (x /= 10) {
			++length;
		}
		return length;
	}();

	// Create a temporary array for storing the message string (null terminated c-string)
	std::array<char, str.size() + 1 + intBase10Digits> s{};
	std::copy(str.cbegin(), str.cend(), s.begin());
	snprintf(s.begin() + str.size(), s.size() - str.size(), "%u", invocation);
	auto m = omnetpp::cMessage(s.cbegin());

	// Request an updated version of the interface inputs
	for (int i = 0; i < interfaceInputGateSize; ++i) {
		auto* g = gate(interfaceInputId + i);
		send(m.dup(), g);
	}

	// Set an updated version of the interface output.
	for (int i = 0; i < interfaceOutputGateSize; ++i) {
		auto* g = gate(interfaceOutputId + i);
		send(m.dup(), g);
	}

	bubble(std::cbegin(s));
	++invocation;
	scheduleAt(omnetpp::simTime() + omnetpp::SimTime(50, omnetpp::SIMTIME_MS), invocationMsg);
}