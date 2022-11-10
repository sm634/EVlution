# EV charging simulation

## Summary

A simple model of Electric Vehical agents moving around a space. Overtime they move between locations and use their battery charge, then go to find a charge point. The model was based on some introductory mesa examples found here: [Intro Tutorial](http://mesa.readthedocs.io/en/latest/intro-tutorial.html).

As the model runs, the agents move around loosing charge, when they get to their desired location they update where they want to go next, then when they start running out of charge they seek a charging point.

## How to Run

ensure you have the requirments installed then open the source folder location and run

```
    $ python run.py
```

Guide to the server as described in the (http://mesa.readthedocs.io/en/latest/intro-tutorial.html#adding-visualization), run:


If your browser doesn't open automatically, point it to [http://127.0.0.1:8521/](http://127.0.0.1:8521/). When the visualization loads, press Reset, then Run.


## Files

* ``run.py``: launches the server
* ``local_run.py``: run model inside python ide
* ``model\model.py``: contains overal model behaviours which then calls agent modules
* ``model\EVAgent.py``: EV agent code/behaviours
* ``model\ChargePoint.py``: Charging Point agent code/behaviours
* ``model\server.py``: server set up details
* ``model\simple_continuous_canvas.js``: bespoke java script to create the plot in the visualisation
* ``model\SimpleContinuousModule.py``: bespoke graph instance instead of using mesa pre built to create the continuous grid plot in the visualisation




## Further Reading

The full tutorial describing how the model is built can be found at:
http://mesa.readthedocs.io/en/latest/intro-tutorial.html

This model is drawn from econophysics and presents a statistical mechanics approach to wealth distribution. Some examples of further reading on the topic can be found at:

[Milakovic, M. A Statistical Equilibrium Model of Wealth Distribution. February, 2001.](https://editorialexpress.com/cgi-bin/conference/download.cgi?db_name=SCE2001&paper_id=214)

[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
____
You will need to open the file as a Jupyter (aka iPython) notebook with an iPython 3 kernel. Required dependencies are listed in the provided `requirements.txt` file which can be installed by running `pip install -r requirements.txt`
