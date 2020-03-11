default = {
    "fuel_econ" : 6377.16, #meters per liter, subject to change
    "day_keys" : ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "cost_params" : {
        "fuel" : [0.6446, 0.6446, 0.6446, 0.6446, 0.6446], #dollars per liter
        "labor" : [0.00417, 0.00417, 0.00417, 0.00417, 0.00417] #dollars per second
    },
    "crew_params" : [None, None, None, None, None],
    #     {0 : None},
    #     {0 : None},
    #     {0 : None},
    #     {0 : None},
    #     {0 : None}
    # ],
    "fuel_const" : [60.567, 60.567, 60.567, 60.567, 60.567],
    # "fuel_const" : [7.567, 7.567, 7.567, 7.567, 7.567],
    #     {0 : 80467},
    #     {0 : 80467},
    #     {0 : 80467},
    #     {0 : 80467},
    #     {0 : 80467}
    # ],
    "time_const" : [25000, 25000, 25000, 25000, 25000]
    #     {0 : 28800},
    #     {0 : 28800},
    #     {0 : 28800},
    #     {0 : 28800},
    #     {0 : 28800}
    # ]
}
