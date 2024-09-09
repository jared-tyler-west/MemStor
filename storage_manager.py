import os
import time

def get_partition_info(mounted_only=False):
    partitions = []
    with os.popen("lsblk -o NAME,SIZE,MOUNTPOINT") as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            details = line.strip().split()
            if len(details) >= 2:
                name = details[0]
                size = details[1]
                mountpoint = details[2] if len(details) == 3 else None

                # If mounted_only is True, skip partitions that are not mounted
                if mounted_only and not mountpoint:
                    continue

                # Fetch the used size using df if the partition is mounted
                used_size = get_used_size(mountpoint) if mountpoint and mountpoint != "unmounted" else "0G"

                partitions.append({
                    "name": name,
                    "size": size,
                    "used_size": used_size,
                    "mountpoint": mountpoint if mountpoint else "unmounted"
                })
    return partitions

def get_used_size(mountpoint):
    """Get the used size of a partition using the 'df' command."""
    try:
        with os.popen(f"df -h {mountpoint} | awk 'NR==2 {{print $3}}'") as f:
            used_size = f.read().strip()
        return used_size
    except Exception as e:
        return "0G"

def get_available_devices():
    devices = []
    # Use lsblk to find available devices that are not mounted
    with os.popen("lsblk -o NAME,SIZE,MOUNTPOINT | grep -v 'MOUNTPOINT'") as f:
        lines = f.readlines()
        for line in lines:
            details = line.strip().split()
            if len(details) == 2:  # Unmounted devices have no MOUNTPOINT
                name, size = details
                devices.append({"name": name, "size": size})
    return devices

def mount_partition(device_name, mount_point):
    try:
        os.system(f"sudo mount /dev/{device_name} {mount_point}")
        return True
    except Exception as e:
        return False
    
def unmount(device_name):
    try:
        os.system(f"sudo umount /dev/{device_name}")
        return True
    except Exception as e:
        return False

def format_device(device_name, filesystem):
    try:
        os.system(f"sudo mkfs.{filesystem} /dev/{device_name}")
        return True
    except Exception as e:
        return False

def get_largest_files(directory):
    try:
        with os.popen(f"sudo du -ah {directory} | sort -rh | head -n 10") as f:
            largest_items = f.readlines()
        return [item.strip() for item in largest_items]
    except Exception as e:
        return []

def fsck(device_name):
    try:
        os.system(f"sudo fsck /dev/{device_name}")
        return True
    except Exception as e:
        return False

def get_smart_info(device_name):
    try:
        with os.popen(f"sudo smartctl -a /dev/{device_name}") as f:
            return f.readlines()
    except Exception as e:
        return ["Error retrieving SMART data"]

import time

def monitor_disk_usage(threshold, selected_partitions):
    try:
        while True:
            # Check disk usage for selected partitions using df
            for partition in selected_partitions:
                mountpoint = partition['mountpoint']

                # Get usage percentage using df and parse the output
                df_output = os.popen(f"df -h {mountpoint}").readlines()

                if len(df_output) < 2:
                    print(f"Error: Could not retrieve data for {mountpoint}")
                    continue

                # Parse the correct line (second line) and extract the usage percentage
                usage_line = df_output[1]
                usage_percent = usage_line.split()[4].strip('%')  # Extract the fifth column and remove '%'

                # Validate and parse the usage percentage
                try:
                    usage = int(usage_percent)
                except ValueError:
                    print(f"Error parsing usage for {mountpoint}")
                    usage = 0

                # Check if usage exceeds threshold and print a warning if it does
                if usage >= threshold:
                    print(f"Warning: Disk usage on {mountpoint} is {usage}% (threshold: {threshold}%)")

            time.sleep(60)  # Check every 60 seconds
    except Exception as e:
        print(f"Error during monitoring: {e}")
        return False
    return True