"""Cellular-automaton development for genetic programming.

A parallel research track to the folding pipeline. The CA rule IS the program:
inputs are encoded as a clamped boundary row, the rule is iterated for T steps,
outputs are read from a designated cell.

Sweep-first: every axis is a field on CAConfig; experiments are pure functions
of that config.
"""
