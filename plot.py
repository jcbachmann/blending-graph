#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import code
import csv
import datetime
import io
import logging
import matplotlib
import numpy
import re
import sys
import matplotlib.pyplot
import glob
from matplotlib.ticker import FormatStrFormatter

def get_arrays_to_plot(pool, xind, yind):
	x, y = [], []
	cnt = 0

	for res in pool:
		try:
			cnt += 1
			xval = res[xind]
			yval = res[yind]
			xt = float(xval)
			yt = float(yval)
			if xt is None or yt is None:
				print("could not process line %s" % res)
				continue
			x.append(xt)
			y.append(yt)
		except Exception as e:
			print(type(res))
			print("problem handling line %d: %s" % (cnt, res))
			raise e

	return x, y

def do_once_per_graph(subplot, x, y, label="some data", color="black", linestyle="solid"):
	subplot.plot(x, y, color=color, antialiased=True, label=label, linestyle=linestyle)

	dx = numpy.amax(x) - numpy.amin(x)
	dy = numpy.amax(y) - numpy.amin(y)
	subplot.set_xlim([numpy.amin(x) - 0.05 * dx, numpy.amax(x) + 0.05 * dx])
	subplot.set_ylim([numpy.amin(y) - 0.05 * dy, numpy.amax(y) + 0.05 * dy])
	
def do_once_per_graph_scatter(subplot, x, y, label="some data", color="black"):
	subplot.scatter(x, y, color=color, antialiased=True, label=label, marker="x")

	dx = numpy.amax(x) - numpy.amin(x)
	dy = numpy.amax(y) - numpy.amin(y)
	minv = min(numpy.amin(x) - 0.05 * dx, numpy.amin(y) - 0.05 * dy)
	maxv = max(numpy.amax(x) + 0.05 * dx, numpy.amax(y) + 0.05 * dy)
	subplot.set_xlim([minv, maxv])
	subplot.set_ylim([minv, maxv])
	#subplot.set_xlim([numpy.amin(x) - 0.05 * dx, numpy.amax(x) + 0.05 * dx])
	#subplot.set_ylim([numpy.amin(y) - 0.05 * dy, numpy.amax(y) + 0.05 * dy])

def prepare_matplotlib():
	numpy.set_printoptions(linewidth=200)
	numpy.set_printoptions(suppress=True)
	numpy.set_printoptions(precision=5)

	figure = matplotlib.pyplot.figure(figsize=(8, 6))
	subplot = figure.add_subplot(111)
	return subplot

if __name__ == '__main__':
	subplot = prepare_matplotlib()
	subplot2 = prepare_matplotlib()

	ySums = [0, 0, 0]

	arg = []

	if len(sys.argv) == 2:
		arg1 = glob.glob(sys.argv[1] + "/*stack.csv.sim.slices.csv")
		arg2 = glob.glob(sys.argv[1] + "/*reclaim.csv.slices.csv")
		if len(arg1) == 1 and len(arg2) == 1:
			arg = [arg1[0], arg2[0]]
	elif len(sys.argv) == 3:
		arg = sys.argv[1:]
	
	if len(arg) != 2:
		print("Usage: " + sys.argv[0] + " dir|(stack reclaim)")
		sys.exit(1)

	alltext_sim = open(arg[0]).read()
	alltext_real = open(arg[1]).read()

	x_sim_red, y_sim_red = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_sim), delimiter='\t'), "pos", "red")
	x_sim_blue, y_sim_blue = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_sim), delimiter='\t'), "pos", "blue")
	x_sim_yellow, y_sim_yellow = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_sim), delimiter='\t'), "pos", "yellow")
	
	x_real_red, y_real_red = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_real), delimiter='\t'), "pos", "red")
	x_real_blue, y_real_blue = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_real), delimiter='\t'), "pos", "blue")
	x_real_yellow, y_real_yellow = get_arrays_to_plot(csv.DictReader(io.StringIO(alltext_real), delimiter='\t'), "pos", "yellow")
	
	for i in range(0, 5):
		y_sim_red = numpy.convolve(y_sim_red, [0.25, 0.5, 0.25], mode='same')
	
	for i in range(0, 5):
		y_sim_blue = numpy.convolve(y_sim_blue, [0.25, 0.5, 0.25], mode='same')
	
	for i in range(0, 5):
		y_sim_yellow = numpy.convolve(y_sim_yellow, [0.25, 0.5, 0.25], mode='same')
	
	for i in range(0, 50):
		y_real_red = numpy.convolve(y_real_red, [0.25, 0.5, 0.25], mode='same')
	
	for i in range(0, 50):
		y_real_blue = numpy.convolve(y_real_blue, [0.25, 0.5, 0.25], mode='same')
	
	for i in range(0, 50):
		y_real_yellow = numpy.convolve(y_real_yellow, [0.25, 0.5, 0.25], mode='same')
	
	y_real_red = numpy.multiply(y_real_red, sum(y_sim_red) / sum(y_real_red))
	y_real_blue = numpy.multiply(y_real_blue, sum(y_sim_blue) / sum(y_real_blue))
	y_real_yellow = numpy.multiply(y_real_yellow, sum(y_sim_yellow) / sum(y_real_yellow))

	yi_real_red = numpy.interp(x_sim_red, x_real_red, y_real_red)
	yi_real_blue = numpy.interp(x_sim_red, x_real_red, y_real_blue)
	yi_real_yellow = numpy.interp(x_sim_red, x_real_red, y_real_yellow)

	stockpileLength = 70
	do_once_per_graph(subplot, numpy.multiply(x_sim_red, stockpileLength), y_sim_red, label="Red$_{Simulation}$", color="red")
	do_once_per_graph(subplot, numpy.multiply(x_sim_blue, stockpileLength), y_sim_blue, label="Blue$_{Simulation}$", color="blue")
	do_once_per_graph(subplot, numpy.multiply(x_sim_yellow, stockpileLength), y_sim_yellow, label="Yellow$_{Simulation}$", color="green")
	
	do_once_per_graph(subplot, numpy.multiply(x_sim_red, stockpileLength), yi_real_red, label="Red$_{Model}$", color="red", linestyle="dashed")
	do_once_per_graph(subplot, numpy.multiply(x_sim_blue, stockpileLength), yi_real_blue, label="Blue$_{Model}$", color="blue", linestyle="dashed")
	do_once_per_graph(subplot, numpy.multiply(x_sim_yellow, stockpileLength), yi_real_yellow, label="Yellow$_{Model}$", color="green", linestyle="dashed")

	subplot.grid(True)
	subplot.set_title("Stockpile Volume", fontsize=30)
	subplot.set_xlabel("Reclaimer Position", fontsize=20)
	subplot.set_ylabel("Slice Volume", fontsize=20)
	
	subplot.xaxis.set_major_formatter(FormatStrFormatter('%d cm'))
	subplot.yaxis.set_major_formatter(FormatStrFormatter('%d mm³/s'))

	subplot.legend(loc='upper left')

	do_once_per_graph_scatter(subplot2, y_sim_red, yi_real_red, label="Red", color="red")
	do_once_per_graph_scatter(subplot2, y_sim_blue, yi_real_blue, label="Blue", color="blue")
	do_once_per_graph_scatter(subplot2, y_sim_yellow, yi_real_yellow, label="Yellow", color="green")

	subplot2.grid(True)
	subplot2.set_title("Simulation vs. Model", fontsize=30)
	subplot2.set_xlabel("Slice Volume$_{Simulation}$", fontsize=20)
	subplot2.set_ylabel("Slice Volume$_{Model}$", fontsize=20)
	
	subplot2.xaxis.set_major_formatter(FormatStrFormatter('%d mm³/s'))
	subplot2.yaxis.set_major_formatter(FormatStrFormatter('%d mm³/s'))
	subplot2.set_aspect(1)

	subplot2.legend(loc='upper left')

	stddev_red = pow(numpy.sum(numpy.square(numpy.subtract(y_sim_red, yi_real_red))) / len(x_sim_red), .5) / numpy.max(y_sim_red)
	stddev_blue = pow(numpy.sum(numpy.square(numpy.subtract(y_sim_blue, yi_real_blue))) / len(x_sim_blue), .5) / numpy.max(y_sim_blue)
	stddev_yellow = pow(numpy.sum(numpy.square(numpy.subtract(y_sim_yellow, yi_real_yellow))) / len(x_sim_yellow), .5) / numpy.max(y_sim_yellow)
	print("stddev red:     {:5.2f}%".format(stddev_red*100))
	print("stddev blue:    {:5.2f}%".format(stddev_blue*100))
	print("stddev yellow:  {:5.2f}%".format(stddev_yellow*100))
	
	matplotlib.pyplot.show()
