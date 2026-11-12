#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Check the PETSc/MPI environment for the general J-class
traffic Mean-Field Game parallel solver.

Intended for execution on an HPC system such as Toubkal.

Usage:
    python3 check_environment.py

    mpirun -np 2 python3 check_environment.py
"""

import sys

try:
    import mpi4py
    from mpi4py import MPI
except ImportError as exc:
    raise SystemExit(
        "mpi4py is not available in this Python environment."
    ) from exc

try:
    import petsc4py

    petsc4py.init(sys.argv)

    from petsc4py import PETSc

except ImportError as exc:
    raise SystemExit(
        "petsc4py is not available in this Python environment."
    ) from exc


def main():

    comm = MPI.COMM_WORLD

    rank = comm.Get_rank()
    size = comm.Get_size()

    petsc_version = PETSc.Sys.getVersion()

    print(
        f"Rank {rank}/{size} | "
        f"Python {sys.version.split()[0]} | "
        f"mpi4py {mpi4py.__version__} | "
        f"petsc4py {petsc4py.__version__} | "
        f"PETSc {petsc_version}",
        flush=True,
    )

    comm.Barrier()

    if rank == 0:

        print("\nPETSc/MPI environment initialized.")

        print(f"MPI processes: {size}")
        print(f"PETSc version: {petsc_version}")

        print("\nAvailable PETSc solver interfaces:")

        print(
            "SNES:",
            hasattr(PETSc, "SNES"),
        )

        print(
            "KSP:",
            hasattr(PETSc, "KSP"),
        )

        print(
            "Distributed matrices:",
            hasattr(PETSc, "Mat"),
        )

        print(
            "\nNote: This check does not establish "
            "whether PETSc was built with SuperLU_DIST."
        )


if __name__ == "__main__":
    main()
