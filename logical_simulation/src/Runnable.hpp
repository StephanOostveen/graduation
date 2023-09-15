#include <omnetpp.h>

class Runnable : public omnetpp::cSimpleModule {
public:
	Runnable() = default;
	virtual ~Runnable() noexcept;

protected:
	virtual void initialize() override;
	virtual void handleMessage(omnetpp::cMessage* msg) override;

	void handleSelfMessage(omnetpp::cMessage* msg);

private:
	omnetpp::cMessage* invocationMsg{nullptr};
	unsigned           invocation{0};

	int period{0};

	int interfaceInputId{0};
	int interfaceInputGateSize{0};
	int interfaceOutputId{0};
	int interfaceOutputGateSize{0};
};