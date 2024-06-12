import subprocess
from typing import Dict, List


def get_list_of_devices() -> Dict[str, List[str]]:
    res = subprocess.check_output(["v4l2-ctl", "--list-devices"])
    arr = res.decode("utf-8").splitlines()

    dev_per_name = {}

    dev_name = ""
    for line in arr:
        if ":" in line:
            if "V4L2" not in line:
                dev_name = line.split("(")[0]
            else:
                dev_name = ""
        else:
            if dev_name:
                if dev_name not in dev_per_name.keys():
                    dev_per_name[dev_name] = []

                if line:
                    dev_per_name[dev_name].append(line.strip())

    return dev_per_name
