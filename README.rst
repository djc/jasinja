About Jasinja
=============

Jasinja is a compiler for Jinja templates targeting Javascript. I started
it when we wanted to start generating or extending some of the pages in
an internal webapp with dynamic webapp. I have grown rather fond of Jinja's
template syntax, and much prefer it to working with JavaScript (which, in
my experience, is rather limited compared to Python itself). I thus wrote
a proof of concept to have Jinja templates compiled to JavaScript, and
Jinja is the result. It works quite well for the (admittedly limited)
subset of Jinja we use at work, and I hope it may work well for you.

Requirements
============

Jasinja has been tested against Python 2.5, 2.6 and 2.7. It only depends on
Jinja (tested against version 2.6) and setuptools/Distribute. However,
running the test suite has two further requirements: python-spidermonkey
(tested with version 0.0.10) and JSON support. For JSON support, either the
stdlib json module can be used or the simplejson library (the latter is
always preferred when installed).
