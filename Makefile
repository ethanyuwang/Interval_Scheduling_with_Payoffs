all: payoff_sched.cpp 
	g++ -std=c++11 payoff_sched.cpp -o payoff_sched

clean: 
	$(RM) payoff_sched