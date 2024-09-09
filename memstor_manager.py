import curses
import multiprocessing
from storage_manager import get_partition_info, get_available_devices, mount_partition, unmount, format_device, get_largest_files, fsck, monitor_disk_usage, get_smart_info

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Initialize Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    # Main loop
    while True:
        stdscr.clear()

        # Header
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, "MemStor Manager (Alpha Version [v1.0])")
        stdscr.attroff(curses.color_pair(1))

        # Menu Options
        stdscr.addstr(2, 0, "1. View Partition Usage")
        stdscr.addstr(3, 0, "2. Mount Partition")
        stdscr.addstr(4, 0, "3. Unmount Partition")
        stdscr.addstr(5, 0, "4. Format Partition")
        stdscr.addstr(6, 0, "5. Disk Usage Analysis (Space Hog Identification)")
        stdscr.addstr(7, 0, "6. File System Check and Repair")
        stdscr.addstr(8, 0, "7. Disk Health Monitoring (SMART)")
        stdscr.addstr(9, 0, "8. Set Disk Usage Alerts")
        stdscr.addstr(10, 0, "[Q] Quit")

        # Wait for user input
        key = stdscr.getch()

        # Handle user input
        if key == ord('1'):
            view_partition_usage(stdscr)
        elif key == ord('2'):
            assign_partition_to_mount(stdscr)
        elif key == ord('3'):
            unmount_partition(stdscr)
        elif key == ord('4'):
            format_partition(stdscr)
        elif key == ord('5'):
            disk_usage_analysis(stdscr)
        elif key == ord('6'):
            check_and_repair_fs(stdscr)
        elif key == ord('7'):
            disk_health_monitor(stdscr)
        elif key == ord('8'):
            set_disk_usage_alert(stdscr)
        elif key == ord('q'):
            break

        stdscr.refresh()

def disk_health_monitor(stdscr):
    stdscr.clear()

    # Get available devices
    devices = get_available_devices()

    stdscr.addstr(0, 0, "Select a device to view SMART health information:")
    for i, device in enumerate(devices):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {device['name']} ({device['size']})")

    stdscr.addstr(len(devices) + 2, 0, "Enter the number of the device, or 'Q' to go back:")
    key = stdscr.getch()

    if key == ord('q'):
        return

    try:
        selected_device = devices[int(chr(key)) - 1]
    except (ValueError, IndexError):
        stdscr.addstr(len(devices) + 3, 0, "Invalid selection. Press any key to return.")
        stdscr.getch()
        return

    # Display SMART information
    smart_info = get_smart_info(selected_device['name'])

    for i, line in enumerate(smart_info):
        stdscr.addstr(i + 3, 0, line)

    stdscr.addstr(len(smart_info) + 4, 0, "[Press any key to return]")
    stdscr.getch()

def set_disk_usage_alert(stdscr):
    stdscr.clear()

    # Get list of available partitions
    partitions = get_partition_info(mounted_only=True)

    # Display list of partitions
    stdscr.addstr(0, 0, "Select partitions to monitor (separated by commas), or type 'ALL' to monitor all:")
    for i, partition in enumerate(partitions):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {partition['name']} ({partition['mountpoint']})")

    stdscr.addstr(len(partitions) + 2, 0, "Enter your selection: ")
    curses.echo()
    user_input = stdscr.getstr(len(partitions) + 3, 0).decode('utf-8').strip().lower()
    curses.noecho()

    selected_partitions = []
    
    if user_input == 'all':
        selected_partitions = partitions  # Monitor all partitions
    else:
        try:
            # Parse user input and get selected partitions
            indices = [int(index.strip()) - 1 for index in user_input.split(',')]
            selected_partitions = [partitions[i] for i in indices if 0 <= i < len(partitions)]
        except (ValueError, IndexError):
            stdscr.addstr(len(partitions) + 4, 0, "Invalid selection. Press any key to return.")
            stdscr.getch()
            return

    # Prompt user for threshold percentage
    stdscr.addstr(len(partitions) + 5, 0, "Enter the disk usage threshold percentage (e.g., 90): ")
    curses.echo()
    threshold = stdscr.getstr(len(partitions) + 6, 0).decode('utf-8').strip()
    curses.noecho()

    # Validate threshold input
    try:
        threshold = int(threshold)
        if not (0 <= threshold <= 100):
            raise ValueError
    except ValueError:
        stdscr.addstr(len(partitions) + 7, 0, "Invalid threshold. Must be a number between 0 and 100.")
        stdscr.addstr(len(partitions) + 8, 0, "[Press any key to return]")
        stdscr.getch()
        return

    # Start monitoring in a background process
    monitor_process = multiprocessing.Process(target=monitor_disk_usage, args=(threshold, selected_partitions))
    monitor_process.start()

    stdscr.addstr(len(partitions) + 9, 0, f"Disk usage alert set at {threshold}% successfully.")
    stdscr.addstr(len(partitions) + 10, 0, "[Monitoring in the background. Press any key to return.]")
    stdscr.getch()

def check_and_repair_fs(stdscr):
    stdscr.clear()

    # Get list of mounted partitions
    partitions = get_partition_info()

    stdscr.addstr(0, 0, "Select a partition to check and repair:")
    for i, partition in enumerate(partitions):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {partition['name']} ({partition['mountpoint']})")

    stdscr.addstr(len(partitions) + 2, 0, "Enter the number of the partition, or 'Q' to go back:")
    key = stdscr.getch()

    if key == ord('q'):
        return

    try:
        selected_partition = partitions[int(chr(key)) - 1]
    except (ValueError, IndexError):
        stdscr.addstr(len(partitions) + 3, 0, "Invalid selection. Press any key to return.")
        stdscr.getch()
        return

    # Run file system check
    success = fsck(selected_partition['name'])

    if success:
        stdscr.addstr(len(partitions) + 4, 0, f"File system check completed for {selected_partition['name']}.")
    else:
        stdscr.addstr(len(partitions) + 4, 0, f"File system check failed for {selected_partition['name']}.")

    stdscr.addstr(len(partitions) + 5, 0, "[Press any key to return]")
    stdscr.getch()


def disk_usage_analysis(stdscr):
    stdscr.clear()

    stdscr.addstr(0, 0, "Enter the directory to analyze (e.g., /home, /var): ")
    curses.echo()
    directory = stdscr.getstr(1, 0).decode('utf-8')
    curses.noecho()

    stdscr.clear()
    stdscr.addstr(0, 0, f"Analyzing disk usage in {directory}...")

    # Get the top 10 largest files or directories
    largest_items = get_largest_files(directory)

    # Display the results
    for i, item in enumerate(largest_items):
        stdscr.addstr(i + 2, 0, item)

    stdscr.addstr(len(largest_items) + 3, 0, "[Press any key to return]")
    stdscr.getch()


def format_partition(stdscr):
    stdscr.clear()

    # Get available unmounted devices
    devices = get_available_devices()

    stdscr.addstr(0, 0, "Select a device to format:")
    for i, device in enumerate(devices):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {device['name']} ({device['size']})")

    stdscr.addstr(len(devices) + 2, 0, "Enter the number of the device to format, or 'Q' to go back:")
    key = stdscr.getch()

    if key == ord('q'):
        return

    try:
        selected_device = devices[int(chr(key)) - 1]
    except (ValueError, IndexError):
        stdscr.addstr(len(devices) + 3, 0, "Invalid selection. Press any key to return.")
        stdscr.getch()
        return

    stdscr.clear()
    stdscr.addstr(0, 0, "Choose a file system to format the partition (e.g., ext4, ntfs, vfat): ")
    curses.echo()  # Allow user input
    filesystem = stdscr.getstr(1, 0).decode('utf-8')
    curses.noecho()

    # Format the partition
    success = format_device(selected_device['name'], filesystem)

    if success:
        stdscr.addstr(3, 0, f"Formatted {selected_device['name']} as {filesystem} successfully.")
    else:
        stdscr.addstr(3, 0, f"Failed to format {selected_device['name']}.")

    stdscr.addstr(4, 0, "[Press any key to return]")
    stdscr.getch()


def view_partition_usage(stdscr):
    stdscr.clear()
    partitions = get_partition_info()

    # Display Partition Info
    display_partition_bars(stdscr, partitions, 3)

    stdscr.addstr(len(partitions) + 6, 0, "[Press any key to return]")
    stdscr.getch()

def assign_partition_to_mount(stdscr):
    stdscr.clear()

    # Get available devices
    devices = get_available_devices()

    stdscr.addstr(0, 0, "Select a device to mount:")
    for i, device in enumerate(devices):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {device['name']} ({device['size']})")

    stdscr.addstr(len(devices) + 2, 0, "Enter the number of the device to assign, or 'Q' to go back:")
    key = stdscr.getch()

    if key == ord('q'):
        return  # Go back to the main menu

    try:
        selected_device = devices[int(chr(key)) - 1]  # Convert input to int and get device
    except (ValueError, IndexError):
        stdscr.addstr(len(devices) + 3, 0, "Invalid selection. Press any key to return.")
        stdscr.getch()
        return

    stdscr.clear()
    stdscr.addstr(0, 0, f"Selected {selected_device['name']}")
    stdscr.addstr(1, 0, "Enter the mount point (e.g., /mnt/data): ")
    curses.echo()  # Allow user input
    mount_point = stdscr.getstr(2, 0).decode('utf-8')
    curses.noecho()

    # Attempt to mount the device
    success = mount_partition(selected_device['name'], mount_point)

    if success:
        stdscr.addstr(4, 0, f"Mounted {selected_device['name']} to {mount_point} successfully.")
    else:
        stdscr.addstr(4, 0, f"Failed to mount {selected_device['name']} to {mount_point}.")

    stdscr.addstr(5, 0, "[Press any key to return]")
    stdscr.getch()

def unmount_partition(stdscr):
    stdscr.clear()

    # Get list of mounted partitions
    partitions = get_partition_info(mounted_only=True)

    stdscr.addstr(0, 0, "Select a partition to unmount:")
    for i, partition in enumerate(partitions):
        stdscr.addstr(i + 1, 0, f"{i + 1}. {partition['name']} ({partition['mountpoint']})")

    stdscr.addstr(len(partitions) + 2, 0, "Enter the number of the partition to unmount, or 'Q' to go back:")
    key = stdscr.getch()

    if key == ord('q'):
        return

    try:
        selected_partition = partitions[int(chr(key)) - 1]
    except (ValueError, IndexError):
        stdscr.addstr(len(partitions) + 3, 0, "Invalid selection. Press any key to return.")
        stdscr.getch()
        return

    # Attempt to unmount the partition
    success = unmount(selected_partition['name'])

    if success:
        stdscr.addstr(len(partitions) + 4, 0, f"Unmounted {selected_partition['name']} successfully.")
    else:
        stdscr.addstr(len(partitions) + 4, 0, f"Failed to unmount {selected_partition['name']}.")

    stdscr.addstr(len(partitions) + 5, 0, "[Press any key to return]")
    stdscr.getch()


def manage_virtual_storage(stdscr):
    # Placeholder for managing virtual storage, similar to swap management
    stdscr.addstr(0, 0, "Manage Virtual Storage - Not yet implemented")
    stdscr.addstr(2, 0, "[Press any key to return]")
    stdscr.getch()

def display_partition_bars(stdscr, partitions, start_row):
    max_bar_width = 50  # The maximum width for the bar graph
    max_name_width = 15  # Width for partition name column
    max_mount_width = 30  # Width for mountpoint column

    for i, partition in enumerate(partitions):
        name = partition['name']
        size = partition['size']
        used = partition['used_size']
        mountpoint = partition['mountpoint']
        
        # Ensure name and mountpoint have a fixed width
        name = name.ljust(max_name_width)  # Left-justify the partition name
        mountpoint = mountpoint.ljust(max_mount_width)  # Left-justify the mountpoint

        # Safeguard: Strip 'G' or 'M' suffix and ensure sizes are valid integers
        try:
            total_size = int(size[:-1])  # Strip 'G' or 'M' suffix
            used_size = int(used[:-1])   # Strip 'G' or 'M' suffix
        except ValueError:
            total_size = 0  # Default to 0 if there's an error with the size
            used_size = 0  # Default to 0 if there's an error with the used size

        if total_size == 0:
            usage_percentage = 0
        else:
            usage_percentage = (used_size / total_size) * 100

        # Calculate the length of the bar
        bar_length = int((usage_percentage / 100) * max_bar_width)

        # Create the bar string
        bar = "#" * bar_length + "-" * (max_bar_width - bar_length)

        # Display partition name, mountpoint, bar graph, and percentage
        stdscr.addstr(start_row + i, 0, f"{name} ({mountpoint}): [{bar}] {usage_percentage:.2f}% used")


if __name__ == "__main__":
    curses.wrapper(main)
