#include "omnetpp/cgate.h"
#include "omnetpp/cownedobject.h"
#include <omnetpp.h>

class DataDictionary final : public omnetpp::cSimpleModule {
public:
	DataDictionary() = default;
	~DataDictionary() noexcept;

protected:
	virtual void initialize() final;
	virtual void handleMessage(omnetpp::cMessage* msg) final;

private:
	/*
	 * This message is used to simulate a write to the datadict, the write shall occur after all
	 * reads have occured this is realized by giving the message a lower priority. That way the
	 * Future Event Scheduler (FES) will only execute it after all higher priority events with the
	 * same arrival time as the set event have been executed.
	 */
	omnetpp::cMessage* setDelayMsg{nullptr};

	unsigned datadict{0};

	int setGateId{0};
	int getGateInputId{0};
	int getGateOutputId{0};
	int getGateSize{0};

	void handleSetDelay(omnetpp::cMessage* msg);
	void handleSetRequest(omnetpp::cMessage* msg);
	void handleGetRequest(omnetpp::cMessage* msg);
};