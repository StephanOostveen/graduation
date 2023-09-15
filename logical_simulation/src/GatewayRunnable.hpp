#include <omnetpp.h>

#include "Runnable.hpp"
#include "omnetpp/cmessage.h"

class GatewayRunnable final : public Runnable {
public:
	GatewayRunnable() = default;
	virtual ~GatewayRunnable() noexcept;

protected:
	virtual void handleMessage(omnetpp::cMessage* msg) final;

private:
};