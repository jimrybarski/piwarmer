# PiWarmer

The PiWarmer is a book-sized device that controls the temperature of a heating element accoring to an arbitrary, user-defined program. It was developed in the [Finkelstein Lab](http://finkelsteinlab.org/) to regulate the temperature of several experiments that required complex and precise changes in temperature (which commercial solutions surprisingly couldn't provide despite costing significantly more).

This repo contains all source code and configuration files, as well as the schematics for the physical device. We can't build one for you, but you should be able to make your own with limited knowledge of electronics.

## Overview

The PiWarmer is controlled over wifi from any nearby computer through a simple web interface. It works just like most thermocyclers, where you create users and programs. Unlike thermal cyclers, you also have to define the [PID](https://en.wikipedia.org/wiki/PID_controller) values for whatever it is you're heating, since the size, shape and heat capacity of each heating block is unique.

