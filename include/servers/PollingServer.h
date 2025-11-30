#pragma once
#include "IServer.h"

class PollingServer : public IServer {
public:
    bool run(Job* serverJob, std::vector<Job*>& aperiodicQueue, 
             std::vector<TimelineEvent>& history, int currentTime) override;

    std::string getName() const override { return "Polling Server"; }
};