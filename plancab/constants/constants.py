class Constants:
    ride_order_cost = 39
    referrals_for_free_ride = 1  # 3
    referrals_50_percent_off_driver_sub = 3  # 30
    referrals_100_percent_off_driver_sub = 5  # 50
    driver_subscription_cost = 999
    ride_fare = {
        1: {0: 21.89, 1: 2*21.89, 2: 2*20.69,3:239, 4: 17.9, 5: 33.29},
        2: {0: 34.89, 1: 2*34.89, 2: None,3:299, 4: 29.9, 5: 39.89}
    }
    discount_for_office_commute = {7: (0.97,'3%'), 15: (0.97,'3%'), 30: (0.95,'5%')}
