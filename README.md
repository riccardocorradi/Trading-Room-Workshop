## Trading Room Workshop @ _City University of Hong Kong_

In this repository you may find
- a few of the algorithmic trading scripts I (Riccardo) coded and implemented myself for the individual competitions during the course
- the code and presentation of the group project that Me and four other students worked on. Special thanks go to **Elijah Clark** (for helping in the design of the strategy logic) and **Daniel Perez Domouso** (for coding shoulder to shoulder with me in the lab)

# Network programming for algorithmic L/S Equity Trading

## Summary (if you're too busy to read the below)

I took part in an algorithmic trading class during my exchange semester at CityU. I worked with a team of 5 students to develop an algorithm to trade securities.
- Each of us would receive **5 different estimates** of each security's final price at **randomly different times**. Each estimate was subject to an error, for which we were given a formula. 
- We <ins>combined the estimates and errors of all 4 trader interfaces</ins> (thus obtaining min-max ranges for each security's final price), and we were allowed to have more information than any individual trader.
- We would long (short) underpriced (overpriced) securities based on what a server script (one of the four traders) would tell each client (each of the four traders) thanks to a sockets architecture.
- The trading clients continuously rebalanced the books to make sure they were always trading the profit maximising security.

Before the graded competition each time pitched their strategy and forecasted the final rankings of all teams based on the pitches. <u>Our popularity score, calculated on the perception 
that the other teams thought of our pitch, was the highest </u>. Our team was the only one to implement this informational arbitrage strategy, while all other teams replicated the ideas
that the professor suggested - which turned out to underperform in most cases. A team coded something similar, but it required traders to manually input everything into an excel sheet,
while our code only required us to start the server and the clients at the beginning of a simulation.

** We ranked top 3 in all the five graded simulations ** when competing against 13 other teams.

## Introduction: briefing the case
- 70 students were divided into groups of 4/5 people. Each group has 4 computers to trade on a simulated market.
- Each simulated market session lasts five minutes, at the end of which a 'true price' of each security is revealed
- There are two stocks (tickers GEM and UB) in the simulated market + an ETF, based on a basket of 1 unit of each stock
- Each trader gets 5 pieces of news on GEM and 5 pieces of news on UB during each simulation
- Each news message provides an estimate on the security's price at the end of the 5-minutes
- Each estimate is subject to an error, strictly dependent on what time the news message was sent, for which the formula is given
- From each estimate you can compute a minimum and a maximum final price for the security, since you know the formula for the error
- Each time you get a new range for the final stock price, you combine it with the previously obtained ranges and get a tighter one
- Idea: you buy (sell) a security if you see that its spot price is below (above) the minimum (maximum) of your range

## Part 1 of our idea: using network programming
- Traders don't all get the same information, and they get it at random times.
- Why make each trader act based ONLY on the information they received, when each team has 4 traders that could share information?

- We make all traders (the clients) send all new information to one trader (the server) via a simple socket architecture
- Each time traders get new info, they send their latest info (estimate and timestamp) to the server 
- The server computes the most updated price ranges for each security and the minimum guaranteed profit of trading one security (minimum price - spot or spot - maximum price)
- Clients trade the security with the highest minimum expected profit - leveraging the power of 4 times more information than an individual trader's, leaving all other traders behind the curve
- Clients continuously receive and send information thanks to the use of two threads: one to send information, one to receive and trade

  - When a security is underpriced (overpriced) we submit a limit buy (sell) order at the minimum (maximum) of the interval, crossing the ask (bid) side of the order book AND
  - We also send a limit sell (buy) at the maximum (minimum) of the interval. Why? If volatility picks up, we want to be able to sell at the maximum and free up our position limits
  - The orders are deleted and replaced every time new numbers are received from the server
  - Clients also check if they have any unfilled outstanding orders - if they don't, they submit limit buys and sells and the minimum and maximum of the most updated interval of the traded security

## Part 2 of our idea: continuously rebalancing the book
- Sometimes the clients pick a security that later turns out not to be the one granting the highest minimum guaranteed profit
- How? New news are released showing a massive mispricing and/or spot prices move
- Each client has a limit of gross exposure of 100.000 shares; to maximise profits, you always want to be sure that you're using it all to trade the most profitable security
- Solution: we continuously compare the traded security's minimum guaranteed profit to available opportunities on the other two securities
- Potential improvements: implementing a VWAP-based estimation of transaction costs to move away from one security to the others, instead of using security-specific arbitrary values like we did.

# Results
We ran 100 simulations of the strategy's performance prior to the 5 graded competitions, and most times, we achieved better P&L than a trader with a 100% hit ratio always trading the most profitable security on a buy-and-hold basis. 
This was mainly the case in situations where we'd trade one security and then switch to another, entering the new position with some extra P&L. We tested the statistical significance of this through a bootstrap-based difference in means test comparing the
mean percentage difference in profits between our strategy and that of the perfect-foresight trader. (see the slides for more details)

In the graded simulations, we consistently achieved a team P&L (based on average profits of the four traders) within the top 3.

Furthermore, each team was required to pitch the strategy to the class, a few weeks before the final competitions. Each team would then try to predict the 
final rankings of the competition, by sending the teacher their view on team rankings. Each team would thus be assigned a popularity score (based on what other teams predicted would be
their ranking) and a prediction score (based on how accurate their prediction score was of the final rankings). 
We achieved top 1 popolarity score and our presentation lasted a lot longer than expected, since we were asked more questions than any other team.




