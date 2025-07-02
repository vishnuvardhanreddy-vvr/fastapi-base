from newrelic import agent

class Monitor:
    def __init__(self):
        agent.initialize()