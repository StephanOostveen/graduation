#include "omnetpp/cmessage.h"
#include "omnetpp/csimplemodule.h"
#include <omnetpp.h>

class DataRouter final : public omnetpp::cSimpleModule {
public:
	DataRouter() = default;
	~DataRouter() noexcept;

protected:
	virtual void initialize() final;
	virtual void handleMessage(omnetpp::cMessage* msg) final;

private:
	int outputGateId{0};
	int outputGateSize{0};
};