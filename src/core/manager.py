from configparser import ConfigParser
from dataclasses import dataclass
import json
import os


@dataclass
class VirtualMachine:
    file: os.DirEntry
    config: ConfigParser


class Manager():

    def list_vms_in_folder(self, folder):
        rv = []
        vm_list = os.scandir(folder)
        for dir in vm_list:
            vm_files = os.scandir(dir.path)
            for f in vm_files:
                if ".conf" in f.name:
                    vm_cfg = ConfigParser()
                    vm_cfg.read(f.path)
                    rv.append(VirtualMachine(file=f, config=vm_cfg))
        return rv

    def launch_vm(self, file: os.DirEntry, config: ConfigParser):
        print("Running VM " + config["VM"]["Name"] + "...")

        pre_lines = []
        pre_lines.extend(self.generate_global_pre_lines(file, config))
        pre_lines.extend(self.generate_nic_pre_lines(file, config))

        arg_lines = []
        arg_lines.extend(self.generate_global_arg_lines(file, config))
        arg_lines.extend(self.generate_nic_arg_lines(file, config))

        print(json.dumps(pre_lines, indent=4))
        print(json.dumps(arg_lines, indent=4))

    def generate_global_pre_lines(self, file: os.DirEntry, config: ConfigParser):
        rv = []
        vm_id = os.path.splitext(file.name)[0]
        rv.append(f"vmname={vm_id}")

        return rv

    def generate_nic_pre_lines(self, file: os.DirEntry, config: ConfigParser):
        rv = []
        vm_id = os.path.splitext(file.name)[0]
        for key in config:
            if "Devices.NIC" in key:
                section_substrings = key.split(".")

                nic = config[key]
                nic_id = section_substrings[-1]

                if nic["Type"] == "tap":
                    nic_eth = nic['Eth']
                    nic_mac = nic['MAC']
                    rv.append(f"eth_{nic_id}={nic_eth}")
                    rv.append(f"mac_{nic_id}={nic_mac}")
                    rv.append(f"ifname_{nic_id}=macvtap_{vm_id}_{nic_id}")
                    rv.append(f"nmcli con del $ifname_{nic_id}")
                    rv.append(f"nmcli con add con-name $ifname_{nic_id} type macvlan dev $eth_{nic_id} mode bridge tap yes ifname $ifname_{nic_id} ipv6.method \"disabled\" ipv4.method \"disabled\"")
                    rv.append(f"ip link set $ifname_{nic_id} address $mac_{nic_id}")
                    rv.append(f"nmcli con up $ifname_{nic_id}")
                    rv.append(f"tap_{nic_id}=$(cat /sys/class/net/$ifname_{nic_id}/ifindex)")
                    rv.append(f"mac_{nic_id}=$(cat /sys/class/net/$ifname_{nic_id}/address)")

        return rv

    def generate_global_arg_lines(self, file: os.DirEntry, config: ConfigParser):
        rv = []
        vm_id = os.path.splitext(file.name)[0]

        gral_kvm = config["General"]["KVM"]
        gral_uefi = config["General"]["UEFI"]
        gral_hpet = config["General"]["HPET"]
        gral_machine = config["General"]["Machine"]
        gral_serial = config["General"]["Serial"]
        gral_parallel = config["General"]["Parallel"]
        gral_keyboard = config["General"]["Keyboard"]
        ram_mb = config["General"]["RAM"]
        cpu_type = config["CPU"]["Type"]
        cpu_sockets = config["CPU.Cores"]["Sockets"]
        cpu_cores = config["CPU.Cores"]["Cores"]
        cpu_threads = config["CPU.Cores"]["Threads"]
        cpu_flags_kvm = config["CPU.Flags"]["KVM"]
        cpu_flags_hypervisor = config["CPU.Flags"]["Hypervisor"]
        cpu_flags_topoext = config["CPU.Flags"]["Topoext"]
        cpu_flags_migratable = config["CPU.Flags"]["Migratable"]
        cpu_flags_hyperv = config["CPU.Flags"]["HyperV"]
        cpu_flags_hyperv_vendorid = config["CPU.Flags"]["HyperV_VendorID"]

        rv.append(f"-name $vmname,process=$vmname,debug-threads=on")
        rv.append(f"-pidfile /tmp/$vmname.pid")
        rv.append(f"-nodefaults")
        rv.append(f"-global kvm-pit.lost_tick_policy=discard")
        rv.append(f"-global ICH9-LPC.disable_s3=1")
        rv.append(f"-global ICH9-LPC.disable_s4=1")

        if (gral_kvm == '1'):
            rv.append(f"-enable-kvm")

        if (gral_hpet == '0'):
            rv.append(f"-no-hpet")

        cpu = []
        cpu.append(f"-cpu {cpu_type}")
        cpu.append("kvm=off" if cpu_flags_kvm == "0" else "kvm=on")
        cpu.append("-hypervisor" if cpu_flags_hypervisor == "0" else "+hypervisor")
        cpu.append("topoext=on" if cpu_flags_topoext == "1" else "topoext=off")
        cpu.append("migratable=yes" if cpu_flags_migratable == "1" else "migratable=no")
        if cpu_flags_hyperv == "1":
            cpu.append("hv-passthrough")
        if cpu_flags_hyperv_vendorid != "":
            cpu.append(f"hv-vendor-id={cpu_flags_hyperv_vendorid}")
        rv.append(",".join(cpu))

        rv.append(f"-machine {gral_machine}")
        rv.append(f"-smp cores={cpu_cores},threads={cpu_threads},sockets={cpu_sockets}")
        rv.append(f"-m {ram_mb}")
        rv.append("-rtc base=localtime,clock=host,driftfix=slew")
        rv.append(f"-k {gral_keyboard}")
        rv.append(f"-monitor stdio")

        if (gral_serial == "0"):
            rv.append(f"-serial none")

        if (gral_parallel == "0"):
            rv.append(f"-parallel none")

        return rv

    def generate_nic_arg_lines(self, file: os.DirEntry, config: ConfigParser):
        rv = []
        vm_id = os.path.splitext(file.name)[0]
        for key in config:
            if "Devices.NIC" in key:
                section_substrings = key.split(".")

                nic = config[key]
                nic_id = section_substrings[-1]

                if nic["Type"] == "tap":
                    nic_mac = nic['MAC']
                    nic_flags = nic['Flags']
                    nic_device = nic['Device']

                    if nic_flags != "":
                        nic_flags = "," + nic_flags

                    # TODO: Autogenerate fd=3
                    # TODO: Autogenerate id=net0
                    rv.append(f"-netdev tap,fd=3,id={nic_id}")
                    rv.append(f"-device {nic_device},netdev={nic_id},id=net0,mac={nic_mac}{nic_flags}")

        return rv
