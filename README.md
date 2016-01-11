# PiWarmer

The PiWarmer is a book-sized device that controls the temperature of a heating element accoring to an arbitrary, user-defined program. It was developed in the [Finkelstein Lab](http://finkelsteinlab.org/) to regulate the temperature of several experiments that required complex and precise changes in temperature (which commercial solutions surprisingly couldn't provide despite costing significantly more).

![alt tag](https://github.com/jimrybarski/piwarmer/blob/master/schematics/images/exterior_pi.jpg)

This repo contains everything you need to make and configure your own. We can't build one for you, but you should be able to build your own with a cursory knowledge of electronics.

## Overview

The PiWarmer is controlled over wifi from any nearby computer through a simple web interface. It works just like most thermocyclers, where you create users and programs. Unlike thermal cyclers, you also have to define the [PID](https://en.wikipedia.org/wiki/PID_controller) values for whatever it is you're heating, since the size, shape and heat capacity of each heating block is unique.

## How to Build

You'll need basic electronics skills. Schematics are provided [here](https://github.com/jimrybarski/piwarmer/blob/master/schematics/README.md) along with the [bill of materials](https://github.com/jimrybarski/piwarmer/blob/master/schematics/bom.md) and some photos of a completed device.

## How to Configure

There are instructions on the wiki for this repo, but we'll add an image that you can just write to the SD drive.