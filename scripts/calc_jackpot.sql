-- group.html - Calculation to total the total jackpot by using the number of participants x entry cost.

select num_of_part * entry_price as jackpot from ss_group where groupid = "group_code";