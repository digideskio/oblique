# Oblique

This was a project to scrape airline flights.  In particular,
it worked at one time for at least two Australian airlines.

The code was created around 2005, and is very poorly documented.

However, it helps to know that the two airlines compared here were JetStar and
Virgin Blue.

The `.wis` files contain state machines which are run by the `Witness` module.

`Witness` uses the `Awkward` module which, if memory serves, is something like
`awk`. `Awkward` in turn uses the `Trespass` module to concurrently
search multiple regular expressions simultaneously.

An example of using the code is in `flights.py` which searched for flights on
1-3 March 2005, departing from Brisbane, Gold Coast, or Ballina, to arrive in
Perth.

The output would have looked something like `output.txt`, although that
file only contains flights for Virgin Blue.  Maybe Jetstar did not fly these
routes, or maybe multi-point flights weren't being parsed correctly for Jetstar
or maybe it was a code-share with its parent Qantas, which could also have
broken the parsing, or maybe the Jetstar website was down at the time.  Maybe
the code should log failures better.
