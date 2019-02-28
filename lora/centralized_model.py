"""
 ALOHA with multiple receivers and capture effect - Exact computation of ALOHA
 Factorial is computed separately for scalability
 Multiple SF

"""
import cvxpy as cp
import numpy as np

# Compute time on air
def time_on_air(SF, mac_payload_size, CRC, IH, DE, Npreamble, code_rate, BW):
    Tsym = np.zeros(len(SF))
    Tpreamble = np.zeros((len(SF), len(mac_payload_size)))
    npayload = np.zeros((len(SF), len(mac_payload_size)))
    Tpayload = np.zeros((len(SF), len(mac_payload_size)))
    time_on_air = np.zeros((len(SF), len(mac_payload_size)))
    max_arrival_rate = np.zeros((len(SF), len(mac_payload_size)))
    for s in range(len(SF)):
        for l in range(len(mac_payload_size)):
            Tsym[s] = (2**SF[s])/BW
            Tpreamble[s,l] = (Npreamble) * Tsym[s]
            npayload[s,l] = 8 + np.max(np.ceil((8*mac_payload_size[l] - 4*SF[s] + 28 + 16*CRC -20*IH)/(4*(SF[s]- 2*DE)))*( code_rate +4),0);
            Tpayload[s,l] = npayload[s,l]*Tsym[s]
            time_on_air[s,l] = Tpreamble[s,l] + Tpayload[s,l] # Time on air according to SF(i) and MAC payload size
            max_arrival_rate[s,l] = duty_cycle/time_on_air[s,l] # Maximal Packet rate of the users with SF(i) and Ta(i)
    return time_on_air, max_arrival_rate

duty_cycle = 0.01 # Duty cycle

# System Parameters
nb_devices = 100 # number of devices
nb_channels = 1 # number of channels
nb_devices_SF =  [50, 15, 15, 10, 5, 5]
SF = [7, 8, 9, 10, 11, 12]              # Spreading Factor
nb_sf = len(SF)

# PHY Parameters
CRC = 1
IH = 0
DE = 1            #
Npreamble = 8     # number of preamble
code_rate = 1   # code rate
BW = 125000       # bandwidth

# MAC payload size
mac_payload_size = [50]

# Time on Air computation
time_on_air, max_arrival_rate = time_on_air(SF, mac_payload_size, CRC, IH, DE, Npreamble, code_rate, BW)

# Consider max payload size and SF12
packet_arrival_per_device = max_arrival_rate[-1, -1]
external_packet_arrival = packet_arrival_per_device * np.random.rand(nb_sf,nb_channels)
# Contruct the problem
p = cp.Variable((nb_sf, nb_channels))

# Form the objective
alpha = cp.Parameter(shape = 1)
alpha.value = [packet_arrival_per_device]

beta = cp.Parameter(shape=1)
beta.value = [nb_devices]

gamma = cp.Parameter(shape=np.shape(external_packet_arrival))
gamma.value = np.array(external_packet_arrival)

delta = cp.Parameter(shape =len(SF))
delta.value = np.array(time_on_air[:,-1])


G_pure_aloha = cp.multiply(cp.multiply(alpha, beta), p)
G_pure_aloha = cp.vstack(G_pure_aloha[i,j]+ gamma[i,j] for i in range(nb_sf) for j in range(nb_channels))
G_pure_aloha = cp.reshape(G_pure_aloha, (nb_sf,nb_channels))
G_pure_aloha = cp.vstack(G_pure_aloha[i, j] * delta[i] for i in range(nb_sf) for j in range(nb_channels))
#G_pure_aloha = cp.vstack(G_pure_aloha[i] * cp.exp(G_pure_aloha[i]) for i in range(nb_sf*nb_channels))
G_pure_aloha = cp.reshape(G_pure_aloha, (nb_sf,nb_channels))
#
objective = cp.Maximize(cp.sum(cp.log(G_pure_aloha)) - 2 * cp.sum(G_pure_aloha))
#objective = cp.Maximize(cp.sum(G_pure_aloha))

contraints = [0 <= p, p <= 1, cp.sum(p) == 1,
              cp.sum(p[0:,:]) >= np.divide(nb_devices_SF[0],nb_devices), cp.sum(p[0:1,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:1]), 
              cp.sum(p[1:,:]) >= np.divide(nb_devices_SF[1],nb_devices), cp.sum(p[0:2,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:2]),
              cp.sum(p[2:,:]) >= np.divide(nb_devices_SF[2],nb_devices), cp.sum(p[0:3,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:3]),
              cp.sum(p[3:,:]) >= np.divide(nb_devices_SF[3],nb_devices), cp.sum(p[0:4,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:4]),
              cp.sum(p[4:,:]) >= np.divide(nb_devices_SF[4],nb_devices), cp.sum(p[0:5,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:5]),
              cp.sum(p[5:,:]) >= np.divide(nb_devices_SF[5],nb_devices), cp.sum(p[0:6,:]) <= np.sum(np.divide(nb_devices_SF,nb_devices)[0:6]),
              ]
#
prob = cp.Problem(objective, contraints)

print("Optimal value", prob.solve())
print("Optimal var")
print(p.value)
print("Norm Throughput:")
print(sum(sum(G_pure_aloha.value)))