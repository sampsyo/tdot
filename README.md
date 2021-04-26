Terminal GraphViz
=================

Super silly hack to draw simple GraphViz graphs in ASCII art. Try it like this:

    $ dot -Tjson0 -Gsplines=ortho < something.dot | python3 tg.py

Those `-Tjson0 -Gsplines=ortho` options are required to make it work.
