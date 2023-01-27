#include <omnetpp.h>

class Runnable final : public omnetpp::cSimpleModule {
public:
	Runnable() = default;
	~Runnable() noexcept;

protected:
	virtual void initialize() final;
	virtual void handleMessage(omnetpp::cMessage* msg) final;

private:
	omnetpp::cMessage* invocationMsg{nullptr};
	unsigned           invocation{0};

	int period{0};

	int interfaceInputId{0};
	int interfaceInputGateSize{0};
	int interfaceOutputId{0};
	int interfaceOutputGateSize{0};
};