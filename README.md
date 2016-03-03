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
