from tuntap import Tun

tt = Tun()

tt.configure(ip="10.0.0.7", mask="24")

raw_input()