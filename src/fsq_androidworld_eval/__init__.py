"""AndroidWorld evaluation for the AMKernel agent stack."""

import os

# AndroidWorld forks only to exec adb; no child reuses the parent's gRPC state.
# gRPC at-fork diagnostics otherwise contaminate AndroidEnv's merged ADB output.
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"

__version__ = "0.1.0"
