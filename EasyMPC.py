
import EasyModell as mpc
import parameter as parameters
from parameter import load_params
import pickle
import os
import numpy as np
from datetime import datetime
import copy



options = {
    'Tariff'        :   {'Variable'          : False},   # [-] TRUE = 'variable' or FALSE = 'fix' -> Decides if Powerprice is variable or fix
#    'time_step'     :   {'time_variable'        : ''},
    'WeatherData':   {'TRY'                  : 'cold'       # [-] 'warm'    -> warmes TRY 2015
                                                            # [-] 'normal'  -> normales TRY 2015
                                                    },      # [-] 'cold' -> kaltes TRY 2015
    'Solve'         :   {'MIP_gap'             : 1,
                        'TimeLimit'            : 60,
                        'TimeLimitMax'         : 35491348,
                        'type'                 : 'gurobi',
                         },

    'PV'            :   {'PV_factor'           : 1.0,      # Rescale PV- Generation P_PV = n_Mod (default: 750) * 330 W * PV_factor
                         },

    'Initial'       : {'T_HP_VL_Init'           : 35 + 273.15,
                       },

    'Sto'           : {'Size'                   : 'Small'   # Define Storage size: Small = 300l, Medium = 500l, Large = 1000l

                       },
### Location of the Single Family House ###
    'Location'      :   {'lat'                  : 52.519*2*3.14/360,            # [°]   Latitude Berlin
                         'lon'                  : 13.408*2*3.14/360,            # [°]   Longitude Berlin
                         'roof_area'            : 35,                           # [m²]  Roof Area
                         'til'                  : 15 * 2 * 3.14 / 360,          # [°]   Dachneigung
                         'azi_1'                : 90 * (2 * 3.14) / (360),      # [°]   Orientation of roof sides (0: south, -: East, +: West)
                         'azi_2'                : -90 * (2 * 3.14) / (360)      # [°]   Orientation of roof sides (0: south, -: East, +: West)
                         },
}
#prediction_horizon = 72
start_time = 8760/2
time_step = 1
total_runtime = 480           # Iterationsschritte       -> Sollte durch 24 teilbar sein
control_horizon = 10
params_opti = {
    'prediction_horizon'    : 24,
    'control_horizon'       : control_horizon,
    'time_step'             : time_step,
    'start_time'            : start_time,
    'total_runtime'         : total_runtime,
}
if control_horizon >= params_opti['prediction_horizon']:
    print('Control Horizon has to be smaller than the prediction horizon')

end = 0
# Define paths and directories for results
path_file = str(os.path.dirname(os.path.realpath(__file__)))
#print(path_file)
dir_results = path_file + "/Results/" + str(datetime.now().strftime('%Y-%m-%d'))
if not os.path.exists(dir_results):
    os.makedirs(dir_results)


# Load Parameter
eco, devs, year = parameters.load_params(options, params_opti)

# save paramater settings of devices an economic assumptions to pickle file
devs_file = dir_results + '/devs.pkl'
eco_file = dir_results + '/eco.pkl'
pickle.dump(devs, open(devs_file, "wb"))
pickle.dump(eco, open(eco_file, "wb"))

# Save solving time of iterations
solving_time = {
    'solving_time':[]
}


# Define variables to be saved
save_optim_results = {
#    'solving_time': [],
    'Q_Sto': [],
    'Q_HP': [],
    'Q_Hou_Dem': [],
    'Q_Hou': [],
    'P_EL': [],
    'P_EL_HP': [],
    'P_EL_Dem': [],
    'Q_Penalty' : [],
    'P_PV': [],
    'T_Air': [],
    'T_Sto': [],
    'Q_Sto_Loss': [],
    'T_HP_VL': [],
    'T_HP_RL': [],
    'T_Hou_VL': [],
    'T_Hou_RL': [],
    'c_total': [],
    'c_grid' : [],
    'total_costs':  [],
    'HP_off'    : [],
    'HP_mode1'  : [],
    'HP_mode2'  : [],
    'Mode'      : [],
    'Q_Sto_Energy' : [],
    'Q_Sto_Power' : [],
    'Q_Sto_Power_Max' : [],
    'total_costs' : [],
    'c_power': [],
    'c_penalty':[],
    'c_revenue':[],
    'T_Mean' : [],
    }

save_results = copy.deepcopy(save_optim_results)
#options['Initial']['T_Sto_Init'] = save_optim_results_opti['T_Sto']
# Time Settings
for iter in range(int(params_opti['total_runtime']/params_opti['control_horizon'])):

    time_series = parameters.load_time_series(params_opti, options)
    print("======================== iteration = " +     str(iter) + " ========================")
    print('New start time is:', params_opti['start_time'])
    if iter == 0:
        T_Sto_Init = devs['Sto']['T_Sto_Init']
    else:
        T_Sto_Init = save_results['T_Sto'][iter-1][end]
    results_optim = mpc.runeasyModell(params_opti, options, eco, time_series, devs, iter, T_Sto_Init)
    print('Optimization is running....')



    params_opti['start_time'] = params_opti['start_time'] + params_opti['control_horizon']
    end = int(params_opti['control_horizon']) - 1



    for res in save_results:
       # for t in range(params_opti['prediction_horizon']):
            save_results[res].append(results_optim[res])
#    options['Initial']['T_Sto'] = save_optim_results_opti['T_Sto'][end - 1]


show = 'Heat'

if show == 'HP':
    print('Mode')
    print(save_results['Mode'])
    print('Q_HP')
    print(save_results['Q_HP'])
    print('T_HP_VL')
    print(save_results['T_HP_VL'])
    print('T_HP_RL')
    print(save_results['T_HP_RL'])
    print('T_Sto')
    print(save_results['T_Sto'])
    print('T_Air')
    print(save_results['T_Air'])
    #print('P_EL_HP')
    #print(save_optim_results_opti['P_EL_HP'])
    #print('COP_HP')
    #print(save_optim_results_opti['COP_HP'])
elif show == 'Sto':
    print('T_Sto')
    print(save_results['T_Sto'])
    print('Q_Sto_Energy')
    print(save_results['Q_Sto_Energy'])
    print('Q_Sto_Power')
    print(save_results['Q_Sto_Power'])
    print('Q_Sto_Power_Max')
    print(save_results['Q_Sto_Power_Max'])
elif show == 'Power':
    print('P_EL')
    print(save_results['P_EL'])
    print('P_PV')
    print(save_results['P_PV'])
    print('P_EL_HP')
    print(save_results['P_EL_HP'])
elif show == 'costs':
#    print('c_grid')
#    print(save_optim_results_opti['c_grid'])
    print('c_power')
    print(save_results['c_power'])
    print('c_revenue')
    print(save_results['c_revenue'])
    print('c_penalty')
    print(save_results['c_penalty'])
    print('total_costs')
    print(save_results['total_costs'])
elif show == 'Hou':
    print('Q_Hou')
    print(save_results['Q_Hou'])
    print('T_Hou_VL')
    print(save_results['T_Hou_VL'])
    print('T_Hou_RL')
    print(save_results['T_Hou_RL'])
    print('Q_Penalty')
    print(save_results['Q_Penalty'])
elif show == 'Heat':
    print('Q_HP')
    print(save_results['Q_HP'])
    print('Q_Penalty')
    print(save_results['Q_Penalty'])
    print('Q_Sto_Power')
    print(save_results['Q_Sto_Power'])
    print('Q_Hou')
    print(save_results['Q_Hou'])
    print('Q_Hou_Dem')
    print(save_results['Q_Hou_Dem'])
    print('T_Mean')
    print(save_results['T_Mean'])
    print('T_Sto')
    print(save_results['T_Sto'])
#elif show == 'Vergleich':
elif show == 'all':



    fig, ax = plt.subplots()

    # Werte für Tabelle erstellen
    table_data = [
        ["Mode", save_results['Mode']],
        ["Player 2", save_results['Q_HP']],
      #  ["Player 3", 33],
      #  ["Player 4", 25],
      #  ["Player 5", 12]
    ]

    # Tabelle erstellen
    table = ax.table(cellText=table_data, loc='center')
    plt.show()


else:

    print(save_results['T_Air'])
    print(save_results['T_Mean'])


 #   print(save_results['T_Sto'])





