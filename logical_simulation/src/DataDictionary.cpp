#include "DataDictionary.hpp"
#include "omnetpp/cownedobject.h"
#include "omnetpp/csimulation.h"
#include <array>
#include <iterator>
#include <limits>
#include <string_view>

Define_Module(DataDictionary);

DataDictionary::~DataDictionary() noexcept {
	cancelAndDelete(setDelayMsg);
}

void DataDictionary::initialize() {
	setDelayMsg = new omnetpp::cMessage("Datadict set");
	setDelayMsg->setSchedulingPriority(1);

	setGateId       = gateBaseId("set");
	getGateInputId  = gateBaseId("get$i");
	getGateOutputId = gateBaseId("get$o");
	getGateSize     = gateSize("get$o");
}

void DataDictionary::handleMessage(omnetpp::cMessage* msg) {
	if (msg->isSelfMessage()) {
		handleSetDelay(msg);
	} else if (msg->getArrivalGateId() == setGateId) {
		handleSetRequest(msg);
		delete msg;
	} else if (getGateInputId <= msg->getArrivalGateId()
	           && msg->getArrivalGateId() < getGateInputId + getGateSize) {
		handleGetRequest(msg);
		delete msg;
	}
}

void DataDictionary::handleSetDelay(omnetpp::cMessage* msg) {
	++datadict;
	using namespace std::literals::string_view_literals;
	static constexpr auto str             = "Nr of sets: "sv;
	static constexpr auto intBase10Digits = []() noexcept {
		int  length = 1;
		auto x      = std::numeric_limits<decltype(datadict)>::max();
		while (x /= 10) {
			++length;
		}
		return length;
	}();

	// Create a temporary array for storing the message string (null terminated c-string)
	std::array<char, str.size() + 1 + intBase10Digits> s{};
	std::copy(str.cbegin(), str.cend(), s.begin());
	snprintf(s.begin() + str.size(), s.size() - str.size(), "%u", datadict);
	bubble(std::cbegin(s));
}

void DataDictionary::handleSetRequest(omnetpp::cMessage* msg) {
	scheduleAt(omnetpp::simTime(), setDelayMsg);
}

void DataDictionary::handleGetRequest(omnetpp::cMessage* incommingMsg) {
	using namespace std::literals::string_view_literals;
	static constexpr auto intBase10Digits = []() noexcept {
		int  length = 1;
		auto x      = std::numeric_limits<decltype(datadict)>::max();
		while (x /= 10) {
			++length;
		}
		return length;
	}();

	// Create a temporary array for storing the message string (null terminated c-string)
	std::array<char, 1 + intBase10Digits> s{};
	snprintf(std::begin(s), s.size(), "%u", datadict);

	auto gateID    = incommingMsg->getArrivalGateId();
	auto gateIndex = gateID - getGateInputId;

	auto* newMsg = new omnetpp::cMessage(std::cbegin(s));
	send(newMsg, getGateOutputId + gateIndex);
}
