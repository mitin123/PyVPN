from tuntap import Tun

tt = Tun()

tt.configure(subnet="10.0.0.7/24")

raw_input()